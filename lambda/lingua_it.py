"""Frasi in italiano. Stesse funzioni di lingua_en.py e lingua_es.py."""

from comune import cap, cose_aperte, durata, elenco, non_chiusa

CODICE = "it"
MAPPA = "Mappa"
CIAO = "Ciao!"

AIUTO = ("Puoi chiedermi quanto è carica l'auto, dove si trova, "
         "oppure se è tutto a posto. Posso anche chiuderla, chiudere i finestrini "
         "e accendere o spegnere il clima. Cosa vuoi fare?")
NON_CONFIGURATA = ("La skill non è ancora configurata: inserisci email e password "
                   "dell'account Leapmotor nel file config punto json.")
COMANDI_OFF = "I comandi sono disattivati nella configurazione della skill."
SERVE_PIN = "Per i comandi serve il PIN del veicolo nel file di configurazione."
IMPREVISTO = "Qualcosa è andato storto mentre interrogavo l'auto. Riprova tra poco."

ERRORI = {
    "rete": "Il cloud Leapmotor non risponde in questo momento. Riprova tra poco.",
    "credenziali": ("Non riesco ad accedere all'account Leapmotor. "
                    "Controlla email e password nel file di configurazione della skill."),
    "certificati_app": ("Mancano i certificati dell'app Leapmotor nella cartella lambda. "
                        "Trovi le istruzioni nella pagina del progetto."),
    "certificato": "Il cloud Leapmotor ha mandato un certificato che non riesco ad aprire.",
    "pin": ("Il cloud Leapmotor non ha accettato il PIN. Controllalo nel file di configurazione "
            "prima di riprovare: troppi tentativi sbagliati possono bloccare i comandi remoti."),
    "non_consentito": "Leapmotor non consente questo comando a distanza per la tua auto.",
    "sessione": "La sessione con il cloud Leapmotor è scaduta. Riprova.",
    "server": "Il cloud Leapmotor ha risposto con un errore. Riprova tra poco.",
}

RUOTE = {"ant_sx": "anteriore sinistra", "ant_dx": "anteriore destra",
         "post_sx": "posteriore sinistra", "post_dx": "posteriore destra"}
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
        "agosto", "settembre", "ottobre", "novembre", "dicembre"]

CONFERMA_STATO = " Tra un minuto chiedimi se è tutto a posto per la conferma."


# ---- Grammatica ---------------------------------------------------------------

def al_percento(n):
    """ "al 50 per cento", ma "all'80 per cento": l'articolo segue il suono del numero."""
    vocale = n in (1, 8, 11) or 80 <= n <= 89
    return ("all'%d per cento" if vocale else "al %d per cento") % n


def soggetto(nome):
    """Il nome dell'auto, o "l'auto". Sempre al femminile, come in italiano
    si fa con le auto anche quando il nome e' di marca ("la Ferrari")."""
    return nome or "l'auto"


def a_soggetto(nome):
    """ "all'auto", "a Elettra Lamborghini", "ad Alba"."""
    if not nome:
        return "all'auto"
    return ("ad " if nome[:1].lower() == "a" else "a ") + nome


def _durata(minuti):
    return durata(minuti, "un'ora", "%d ore", "un minuto", "%d minuti", "e")


# ---- Stato --------------------------------------------------------------------

def batteria(s, nome=None):
    if s.soc is None:
        return "Non ricevo il livello della batteria dall'auto."
    if nome:
        frase = "%s è carica %s" % (nome, al_percento(s.soc))
        if s.autonomia_km:
            frase += ", con circa %d chilometri di autonomia" % s.autonomia_km
    else:
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


def indirizzo(a):
    """Dal JSON di Nominatim a "in Via Roma 12, a Bologna"."""
    via = a.get("road") or a.get("pedestrian") or a.get("square")
    civico = a.get("house_number")
    paese = (a.get("city") or a.get("town") or a.get("village")
             or a.get("municipality") or a.get("hamlet"))
    parti = []
    if via:
        parti.append("in %s %s" % (via, civico) if civico else "in %s" % via)
    if paese:
        parti.append("a %s" % paese)
    return ", ".join(parti) or None


def posizione(s, luogo, dove, nome=None):
    """`luogo`: nome di un luogo di config.json; `dove`: frammento da indirizzo()."""
    chi = cap(soggetto(nome))
    if s.lat is None or s.lon is None:
        return "%s non comunica la posizione in questo momento." % chi
    movimento = " ed è in movimento" if s.in_movimento else ""
    if luogo:
        return "%s è %s%s." % (chi, luogo, movimento)
    if dove:
        return "%s si trova %s%s." % (chi, dove, movimento)
    frase = ("Non riesco a ricavare l'indirizzo %s, ma trovi la posizione nella scheda dell'app Alexa."
             % ("di " + nome if nome else "dell'auto"))
    if s.in_movimento:
        frase += " %s è in movimento." % chi
    return frase


def _voci(s):
    voci = []
    for v in cose_aperte(s):
        if v == "portiera":
            voci.append("una portiera aperta")
        elif v == "finestrino":
            voci.append("un finestrino aperto")
        elif v == "baule":
            voci.append("il baule aperto")
        else:
            ruote = [RUOTE[r] for r in s.gomme_anomale]
            if len(ruote) == 1:
                voci.append("una pressione anomala sulla gomma %s" % ruote[0])
            else:
                voci.append("una pressione anomala sulle gomme %s" % elenco(ruote, "e"))
    return voci


def clima(s):
    """Solo se il clima e' acceso: non e' un'anomalia, ma e' bene saperlo."""
    if not s.clima_acceso:
        return ""
    if s.temp_clima:
        return "Il clima è acceso a %d gradi." % s.temp_clima
    return "Il clima è acceso."


def anomalie(s, nome=None, sottinteso=False):
    """sottinteso=True: il soggetto non si ripete ("Tutto a posto: è chiusa a chiave…")."""
    chi = "" if sottinteso else soggetto(nome) + " "
    voci = _voci(s)
    if voci:
        frase = "Attenzione: %sha %s" % (chi, elenco(voci, "e"))
        if non_chiusa(s):
            frase += ", e non è chiusa a chiave"
        frase += "."
    elif non_chiusa(s):
        frase = "Attenzione: %snon è chiusa a chiave." % chi
    elif s.in_movimento:
        frase = "Nessuna anomalia: %sè in movimento, con portiere e finestrini chiusi." % chi
    elif s.chiusa:
        frase = "Tutto a posto: %sè chiusa a chiave, con finestrini e baule chiusi." % chi
    else:
        frase = "Tutto a posto: portiere, finestrini e baule sono chiusi."
    c = clima(s)
    return frase + (" " + c if c else "")


def eta(quando, oggi, ieri):
    orario = "%d e %02d" % (quando.hour, quando.minute) if quando.minute else "%d" % quando.hour
    if quando.date() == oggi:
        giorno = "di oggi"
    elif quando.date() == ieri:
        giorno = "di ieri"
    else:
        giorno = "del %d %s" % (quando.day, MESI[quando.month - 1])
    return "L'ultimo contatto con l'auto è %s alle %s." % (giorno, orario)


# ---- Comandi ------------------------------------------------------------------

def in_movimento(nome):
    return "%s è in movimento: non la chiudo a distanza." % cap(soggetto(nome))


def gia_chiusa(nome):
    return "%s è già chiusa a chiave." % cap(soggetto(nome))


AVVISO_PORTIERA = "Attenzione, risulta una portiera aperta: la chiusura potrebbe non riuscire. "


def chiusa_fatto(nome):
    return "Fatto: %s è chiusa a chiave." % soggetto(nome)


def chiusa_inviato(nome):
    return "Ho mandato %s il comando di chiusura." % a_soggetto(nome) + CONFERMA_STATO


FINESTRINI_GIA = "I finestrini sono già chiusi."
FINESTRINI_FATTO = "Fatto: finestrini chiusi."


def finestrini_inviato(nome):
    return "Ho mandato %s la chiusura dei finestrini." % a_soggetto(nome) + CONFERMA_STATO


SPENTO_GIA = "Il clima è già spento."
SPENTO_FATTO = "Fatto: clima spento."


def spento_inviato(nome):
    return "Ho mandato %s lo spegnimento del clima." % a_soggetto(nome) + CONFERMA_STATO


_IMPIANTI = {"clima": ("clima", "acceso"), "caldo": ("riscaldamento", "acceso"),
             "freddo": ("aria condizionata", "accesa")}


def acceso_fatto(impianto, gradi):
    nome, acceso = _IMPIANTI[impianto]
    return "Fatto: %s %s a %d gradi." % (nome, acceso, gradi)


def acceso_inviato(nome, impianto, gradi):
    return "Ho mandato %s: %s a %d gradi." % (a_soggetto(nome), _IMPIANTI[impianto][0], gradi) + CONFERMA_STATO


TEMP_NON_CAPITA = "Non ho capito la temperatura."


def temp_fuori(minimo, massimo):
    return "Posso impostare il clima tra %d e %d gradi." % (minimo, massimo)
