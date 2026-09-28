"""
Dallo stato grezzo del cloud alle frasi che Alexa pronuncia.

Tutto qui dentro e' puro (niente rete): si prova in locale con uno stato
salvato, senza account ne' Alexa.
"""

import math
import time
from datetime import datetime, timedelta, timezone

# Oltre quest'eta' il dato viene dichiarato: se l'auto e' ferma da giorni,
# "e' chiusa" vale per l'ultima volta che si e' fatta sentire.
DATO_VECCHIO_ORE = 6

RUOTE = [
    ("anteriore sinistra", "leftFrontTirePressure"),
    ("anteriore destra", "rightFrontTirePressure"),
    ("posteriore sinistra", "leftRearTirePressure"),
    ("posteriore destra", "rightRearTirePressure"),
]


class Stato:
    """I soli campi che servono alla skill, gia' interpretati."""

    def __init__(self, data):
        signal = data.get("signal") if isinstance(data.get("signal"), dict) else {}

        # C10/B10 espongono gli id numerici dei segnali, la T03 i campi con nome.
        def num(signal_id, named):
            if signal_id in signal:
                return _to_float(signal[signal_id])
            if named in data:
                return _to_float(data[named])
            return None

        def flag(signal_id, named):
            v = num(signal_id, named)
            return v is not None and v != 0

        soc = num("100003", "soc")
        if soc is None:
            soc = num("1204", "batteryLevel")
        self.soc = _to_int(soc)
        rng = num("3260", "expectedMileage")
        if rng is None:
            rng = num("2188", "liveRemainingRange")
        self.autonomia_km = _to_int(rng)

        # 1149: 0 scollegato, 1 collegato, 2 in carica, 5 cavo durante la marcia.
        charge_state = _to_int(num("1149", "chargeState"))
        current = num("1178", "batteryCurrent")
        gear = _to_int(num("1010", "gearStatus")) or 0
        speed = num("1319", "speed") or 0.0
        self.in_movimento = speed > 2.0 or gear != 0
        self.cavo_collegato = charge_state not in (None, 0, 5)
        self.in_carica = (self.cavo_collegato and not self.in_movimento
                          and current is not None and abs(current) >= 0.5)
        self.minuti_a_fine_carica = _to_int(num("1200", "chargeRemainTime"))
        self.limite_carica = _to_int(num("-", "chargesocSetting"))

        self.finestrini_aperti = any(
            (num(s, n) or 0) > 0 for s, n in (
                ("3727", "leftFrontWindowPercent"), ("3728", "rightFrontWindowPercent"),
                ("1879", "leftRearWindowPercent"), ("1880", "rightRearWindowPercent"))
        ) or any(
            flag(s, n) for s, n in (
                ("1693", "driverWindowStatus"), ("1694", "rightFrontWindowStatus"),
                ("1695", "leftRearWindowStatus"), ("1696", "rightRearWindowStatus"))
        )
        self.portiere_aperte = any(
            flag(s, n) for s, n in (
                ("1277", "lbcmDriverDoorStatus"), ("1278", "rbcmDriverDoorStatus"),
                ("1279", "lbcmLeftRearDoorStatus"), ("1280", "rbcmRightRearDoorStatus"))
        )
        self.baule_aperto = flag("1281", "bbcmBackDoorStatus")
        locked = num("1298", "driverDoorLockStatus")
        self.chiusa = None if locked is None else locked == 1

        # Il campo di stato vale 0 quando la ruota e' a posto; in piu' un
        # controllo di buon senso sul valore in kPa, per i modelli senza stato.
        self.gomme_anomale = []
        for nome, campo in RUOTE:
            stato = num("-", campo + "State")
            kpa = num("-", campo)
            if (stato is not None and stato != 0) or (kpa is not None and 0 < kpa < 180):
                self.gomme_anomale.append(nome)

        lat = num("3", "latitude")
        if lat is None:
            lat = num("3725", "latitude")
        lon = num("2", "longitude")
        if lon is None:
            lon = num("3724", "longitude")
        self.lat = lat if lat else None
        self.lon = lon if lon else None

        ms = num("-", "collectTimeMs")
        self.rilevato_ms = int(ms) if ms else None


def _to_float(v):
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return None
    return None


def _to_int(v):
    return None if v is None else int(round(v))


# ---- Ora italiana senza dipendenze (su Lambda il database dei fusi non e' garantito) ----

def _ultima_domenica(anno, mese):
    giorno = datetime(anno, mese + 1, 1) - timedelta(days=1) if mese < 12 else datetime(anno, 12, 31)
    return giorno - timedelta(days=(giorno.weekday() + 1) % 7)


def ora_italiana(ms):
    utc = datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).replace(tzinfo=None)
    inizio = _ultima_domenica(utc.year, 3).replace(hour=1)
    fine = _ultima_domenica(utc.year, 10).replace(hour=1)
    return utc + timedelta(hours=2 if inizio <= utc < fine else 1)


# ---- Frasi ------------------------------------------------------------------------

def _durata(minuti):
    ore, mins = divmod(minuti, 60)
    parti = []
    if ore:
        parti.append("un'ora" if ore == 1 else "%d ore" % ore)
    if mins or not ore:
        parti.append("un minuto" if mins == 1 else "%d minuti" % mins)
    return " e ".join(parti)


def nota_eta_dato(s, adesso_ms=None):
    """Frase sull'ultimo contatto con l'auto, solo se il dato e' vecchio."""
    if not s.rilevato_ms:
        return ""
    adesso_ms = adesso_ms or int(time.time() * 1000)
    if adesso_ms - s.rilevato_ms < DATO_VECCHIO_ORE * 3600 * 1000:
        return ""
    quando = ora_italiana(s.rilevato_ms)
    oggi = ora_italiana(adesso_ms).date()
    orario = "%d e %02d" % (quando.hour, quando.minute) if quando.minute else "%d" % quando.hour
    if quando.date() == oggi:
        giorno = "di oggi"
    elif quando.date() == oggi - timedelta(days=1):
        giorno = "di ieri"
    else:
        giorno = "del %d %s" % (quando.day, MESI[quando.month - 1])
    return "L'ultimo contatto con l'auto è %s alle %s." % (giorno, orario)


MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
        "agosto", "settembre", "ottobre", "novembre", "dicembre"]


def al_percento(n):
    """ "al 50 per cento", ma "all'80 per cento": l'articolo segue il suono del numero."""
    vocale = n in (1, 8, 11) or 80 <= n <= 89
    return ("all'%d per cento" if vocale else "al %d per cento") % n


def frase_batteria(s):
    if s.soc is None:
        return "Non ricevo il livello della batteria dall'auto."
    frase = "La batteria è " + al_percento(s.soc)
    if s.autonomia_km:
        frase += ", circa %d chilometri di autonomia" % s.autonomia_km
    frase += "."
    if s.in_carica:
        frase += " È in carica"
        if s.minuti_a_fine_carica:
            frase += " e finisce tra circa %s" % _durata(s.minuti_a_fine_carica)
            if s.limite_carica:
                frase += ", " + al_percento(s.limite_carica)
        frase += "."
    elif s.cavo_collegato:
        frase += " Il cavo è collegato ma non sta caricando"
        if s.limite_carica and s.soc >= s.limite_carica:
            frase += ": ha raggiunto il limite impostato"
        frase += "."
    return frase


def distanza_m(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def luogo_noto(s, luoghi):
    """Il primo luogo di config.json entro il suo raggio, o None."""
    if s.lat is None or s.lon is None:
        return None
    for l in luoghi or []:
        try:
            if distanza_m(s.lat, s.lon, float(l["lat"]), float(l["lon"])) <= float(l.get("raggio_m", 150)):
                return l["nome"]
        except (KeyError, TypeError, ValueError):
            continue
    return None


def frase_indirizzo(indirizzo):
    """Dal JSON di Nominatim a "in Via Roma 12, a Bologna"."""
    if not indirizzo:
        return None
    via = indirizzo.get("road") or indirizzo.get("pedestrian") or indirizzo.get("square")
    civico = indirizzo.get("house_number")
    paese = (indirizzo.get("city") or indirizzo.get("town") or indirizzo.get("village")
             or indirizzo.get("municipality") or indirizzo.get("hamlet"))
    parti = []
    if via:
        parti.append("in %s %s" % (via, civico) if civico else "in %s" % via)
    if paese:
        parti.append("a %s" % paese)
    return ", ".join(parti) or None


def frase_posizione(s, luoghi, indirizzo):
    if s.lat is None or s.lon is None:
        return "L'auto non comunica la posizione in questo momento."
    movimento = " ed è in movimento" if s.in_movimento else ""
    luogo = luogo_noto(s, luoghi)
    if luogo:
        return "L'auto è %s%s." % (luogo, movimento)
    dove = frase_indirizzo(indirizzo)
    if dove:
        return "L'auto si trova %s%s." % (dove, movimento)
    return ("Non riesco a ricavare l'indirizzo, ma trovi la posizione "
            "nella scheda dell'app Alexa%s." % movimento)


def anomalie(s):
    elenco = []
    if s.portiere_aperte:
        elenco.append("una portiera è aperta")
    if s.finestrini_aperti:
        elenco.append("c'è un finestrino aperto")
    if s.baule_aperto:
        elenco.append("il baule è aperto")
    if s.chiusa is False and not s.in_movimento:
        elenco.append("non è chiusa a chiave")
    if s.gomme_anomale:
        ruote = s.gomme_anomale
        if len(ruote) == 1:
            elenco.append("la gomma %s ha una pressione anomala" % ruote[0])
        else:
            elenco.append("le gomme %s hanno una pressione anomala" % _elenco(ruote))
    return elenco


def _elenco(voci):
    return voci[0] if len(voci) == 1 else ", ".join(voci[:-1]) + " e " + voci[-1]


def frase_anomalie(s):
    elenco = anomalie(s)
    if not elenco:
        if s.in_movimento:
            return "Nessuna anomalia: l'auto è in movimento, portiere e finestrini chiusi."
        if s.chiusa:
            return "Tutto a posto: l'auto è chiusa a chiave, con finestrini e baule chiusi."
        return "Tutto a posto: portiere, finestrini e baule sono chiusi."
    testo = _elenco(elenco)
    return "Attenzione: " + testo + "."


def frase_riepilogo(s, luoghi, indirizzo):
    anom = frase_anomalie(s)
    return " ".join([frase_batteria(s), frase_posizione(s, luoghi, indirizzo), anom])


def con_eta(frase, s, adesso_ms=None):
    nota = nota_eta_dato(s, adesso_ms)
    return frase + (" " + nota if nota else "")
