"""
Dallo stato grezzo del cloud alle frasi che Alexa pronuncia.

Qui c'e' la lettura dello stato e cio' che non dipende dalla lingua; le frasi
stanno in lingua_it.py, lingua_en.py e lingua_es.py. Tutto puro (niente rete):
si prova in locale con uno stato salvato, senza account ne' Alexa.
"""

import math
import re
import time
from datetime import datetime, timedelta, timezone

import comune
import lingue
import lingua_it

# Oltre quest'eta' il dato viene dichiarato: se l'auto e' ferma da giorni,
# "e' chiusa" vale per l'ultima volta che si e' fatta sentire.
DATO_VECCHIO_ORE = 6

RUOTE = comune.RUOTE


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

        ac = num("1938", "acSwitch")
        self.clima_acceso = None if ac is None else ac == 1
        self.temp_clima = _to_int(num("2183", "acSetting"))
        self.temp_esterna = num("-", "outdoorTemp")

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


# ---- Ora locale senza dipendenze (su Lambda il database dei fusi non e' garantito) ----

def _ultima_domenica(anno, mese):
    giorno = datetime(anno, mese + 1, 1) - timedelta(days=1) if mese < 12 else datetime(anno, 12, 31)
    return giorno - timedelta(days=(giorno.weekday() + 1) % 7)


def ora_locale(ms, fuso_ore=1):
    """
    Ora solare `fuso_ore` (1 = Italia e Spagna, 0 = Regno Unito e Portogallo)
    piu' l'ora legale europea: dall'ultima domenica di marzo all'ultima di
    ottobre, alle 01:00 UTC, uguale in tutta l'Unione e nel Regno Unito.
    """
    utc = datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).replace(tzinfo=None)
    inizio = _ultima_domenica(utc.year, 3).replace(hour=1)
    fine = _ultima_domenica(utc.year, 10).replace(hour=1)
    return utc + timedelta(hours=fuso_ore + (1 if inizio <= utc < fine else 0))


def ora_italiana(ms):
    return ora_locale(ms, 1)


# ---- Utilita' comuni ------------------------------------------------------------------

al_percento = lingua_it.al_percento  # compatibilita' con i test


def nome_parlato(nome):
    """"ElettraLamborghini" -> "Elettra Lamborghini": attaccato, Alexa lo legge male."""
    nome = re.sub(r"(?<=[a-zàèéìòùáíóúñ])(?=[A-Z])", " ", (nome or "").strip())
    return nome or None


def distanza_m(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _nome_luogo(nome, lingua):
    """Il nome di un luogo di config.json: una stringa, o una per lingua
    ({"it": "a casa", "en": "at home", "es": "en casa"})."""
    if isinstance(nome, dict):
        return nome.get(lingua) or nome.get("it") or next(iter(nome.values()), None)
    return nome


def luogo_noto(s, luoghi, lingua="it"):
    """Il primo luogo di config.json entro il suo raggio, o None."""
    if s.lat is None or s.lon is None:
        return None
    for l in luoghi or []:
        try:
            if distanza_m(s.lat, s.lon, float(l["lat"]), float(l["lon"])) <= float(l.get("raggio_m", 150)):
                return _nome_luogo(l["nome"], lingua)
        except (KeyError, TypeError, ValueError):
            continue
    return None


def anomalie(s):
    """Elenco neutro delle anomalie (vuoto = tutto a posto)."""
    return comune.cose_aperte(s) + (["non_chiusa"] if comune.non_chiusa(s) else [])


# ---- Frasi, nella lingua richiesta ---------------------------------------------------

def frase_batteria(s, nome=None, lingua="it"):
    return lingue.get(lingua).batteria(s, nome)


def frase_posizione(s, luoghi, indirizzo, nome=None, lingua="it"):
    L = lingue.get(lingua)
    dove = L.indirizzo(indirizzo) if indirizzo else None
    return L.posizione(s, luogo_noto(s, luoghi, L.CODICE), dove, nome)


def frase_anomalie(s, nome=None, sottinteso=False, lingua="it"):
    return lingue.get(lingua).anomalie(s, nome, sottinteso)


def frase_riepilogo(s, luoghi, indirizzo, nome=None, lingua="it"):
    # Il nome solo nella prima frase: ripeterlo tre volte suonerebbe strano.
    return " ".join([frase_posizione(s, luoghi, indirizzo, nome, lingua),
                     frase_batteria(s, None, lingua),
                     frase_anomalie(s, nome, sottinteso=True, lingua=lingua)])


def nota_eta_dato(s, adesso_ms=None, lingua="it", fuso_ore=1):
    """Frase sull'ultimo contatto con l'auto, solo se il dato e' vecchio."""
    if not s.rilevato_ms:
        return ""
    adesso_ms = adesso_ms or int(time.time() * 1000)
    if adesso_ms - s.rilevato_ms < DATO_VECCHIO_ORE * 3600 * 1000:
        return ""
    quando = ora_locale(s.rilevato_ms, fuso_ore)
    oggi = ora_locale(adesso_ms, fuso_ore).date()
    return lingue.get(lingua).eta(quando, oggi, oggi - timedelta(days=1))


def con_eta(frase, s, adesso_ms=None, lingua="it", fuso_ore=1):
    nota = nota_eta_dato(s, adesso_ms, lingua, fuso_ore)
    return frase + (" " + nota if nota else "")
