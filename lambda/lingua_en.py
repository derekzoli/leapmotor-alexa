"""English phrases (kilometres and Celsius). Same functions as lingua_it.py."""

from comune import cap, cose_aperte, durata, elenco, non_chiusa

CODICE = "en"
MAPPA = "Map"
CIAO = "Bye!"

AIUTO = ("You can ask me how much charge the car has, where it is, "
         "or whether everything is OK. I can also lock it, close the windows, "
         "and switch the climate control on or off. What would you like to do?")
NON_CONFIGURATA = ("The skill isn't set up yet: enter the Leapmotor account email and "
                   "password in the config dot json file.")
COMANDI_OFF = "Commands are switched off in the skill's configuration."
SERVE_PIN = "Commands need the vehicle PIN in the configuration file."
IMPREVISTO = "Something went wrong while checking the car. Please try again shortly."

ERRORI = {
    "rete": "The Leapmotor cloud isn't responding right now. Please try again shortly.",
    "credenziali": ("I can't sign in to the Leapmotor account. "
                    "Check the email and password in the skill's configuration file."),
    "certificati_app": ("The Leapmotor app certificates are missing from the lambda folder. "
                        "You'll find the instructions on the project page."),
    "certificato": "The Leapmotor cloud sent a certificate I can't open.",
    "pin": ("The Leapmotor cloud didn't accept the PIN. Check it in the configuration file "
            "before trying again: too many wrong attempts can block remote commands."),
    "non_consentito": "Leapmotor doesn't allow this remote command for your car.",
    "sessione": "The session with the Leapmotor cloud has expired. Please try again.",
    "server": "The Leapmotor cloud returned an error. Please try again shortly.",
}

RUOTE = {"ant_sx": "front left", "ant_dx": "front right",
         "post_sx": "rear left", "post_dx": "rear right"}
MESI = ["January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December"]

# Paesi dove il civico precede la via.
_CIVICO_PRIMA = {"gb", "us", "ie", "ca", "au", "nz"}

CONFERMA_STATO = " In a minute, ask me if everything is OK to confirm."


def soggetto(nome):
    return nome or "the car"


def _durata(minuti):
    return durata(minuti, "an hour", "%d hours", "a minute", "%d minutes", "and")


# ---- Stato --------------------------------------------------------------------

def batteria(s, nome=None):
    if s.soc is None:
        return "I'm not getting the battery level from the car."
    if nome:
        frase = "%s is %d percent charged" % (nome, s.soc)
    else:
        frase = "The battery is at %d percent" % s.soc
    if s.autonomia_km:
        frase += ", with about %d kilometres of range" % s.autonomia_km
    frase += "."
    if s.in_carica:
        frase += " It's charging"
        if s.minuti_a_fine_carica:
            frase += " and will be done in about %s" % _durata(s.minuti_a_fine_carica)
            if s.limite_carica:
                frase += ", at %d percent" % s.limite_carica
        frase += "."
    elif s.cavo_collegato:
        frase += " The cable is plugged in but it isn't charging"
        if s.limite_carica and s.soc >= s.limite_carica:
            frase += ": it has reached the set limit"
        frase += "."
    return frase


def indirizzo(a):
    """ "at Piazza Maggiore 1, Bologna" (or "at 12 Baker Street, London")."""
    via = a.get("road") or a.get("pedestrian") or a.get("square")
    civico = a.get("house_number")
    paese = (a.get("city") or a.get("town") or a.get("village")
             or a.get("municipality") or a.get("hamlet"))
    if via and civico:
        via = ("%s %s" % (civico, via)) if a.get("country_code") in _CIVICO_PRIMA else ("%s %s" % (via, civico))
    parti = [p for p in (via, paese) if p]
    return ("at " + ", ".join(parti)) if parti else None


def posizione(s, luogo, dove, nome=None):
    chi = cap(soggetto(nome))
    if s.lat is None or s.lon is None:
        return "%s isn't reporting its location right now." % chi
    movimento = " and is moving" if s.in_movimento else ""
    if luogo:
        return "%s is %s%s." % (chi, luogo, movimento)
    if dove:
        return "%s is %s%s." % (chi, dove, movimento)
    frase = ("I can't work out the address of %s, but you'll find the location on the card "
             "in the Alexa app." % soggetto(nome))
    if s.in_movimento:
        frase += " %s is moving." % chi
    return frase


def _voci(s):
    voci = []
    for v in cose_aperte(s):
        if v == "portiera":
            voci.append("a door open")
        elif v == "finestrino":
            voci.append("a window open")
        elif v == "baule":
            voci.append("the boot open")
        else:
            ruote = [RUOTE[r] for r in s.gomme_anomale]
            if len(ruote) == 1:
                voci.append("unusual pressure in the %s tyre" % ruote[0])
            else:
                voci.append("unusual pressure in the %s tyres" % elenco(ruote, "and"))
    return voci


def clima(s):
    if not s.clima_acceso:
        return ""
    if s.temp_clima:
        return "The climate control is on at %d degrees." % s.temp_clima
    return "The climate control is on."


def anomalie(s, nome=None, sottinteso=False):
    """sottinteso=True: "it" instead of the name, for the summary."""
    chi = "it" if sottinteso else soggetto(nome)
    voci = _voci(s)
    if voci:
        frase = "Warning: %s has %s" % (chi, elenco(voci, "and"))
        if non_chiusa(s):
            frase += ", and it isn't locked"
        frase += "."
    elif non_chiusa(s):
        frase = "Warning: %s isn't locked." % chi
    elif s.in_movimento:
        frase = "No problems: %s is moving, with doors and windows closed." % chi
    elif s.chiusa:
        frase = "All good: %s is locked, with windows and boot closed." % chi
    else:
        frase = "All good: doors, windows and boot are closed."
    c = clima(s)
    return frase + (" " + c if c else "")


def eta(quando, oggi, ieri):
    orario = "%d:%02d" % (quando.hour, quando.minute)
    if quando.date() == oggi:
        giorno = "today"
    elif quando.date() == ieri:
        giorno = "yesterday"
    else:
        giorno = "on %d %s" % (quando.day, MESI[quando.month - 1])
    return "I last heard from the car %s at %s." % (giorno, orario)


# ---- Comandi ------------------------------------------------------------------

def in_movimento(nome):
    return "%s is moving: I won't lock it remotely." % cap(soggetto(nome))


def gia_chiusa(nome):
    return "%s is already locked." % cap(soggetto(nome))


AVVISO_PORTIERA = "Heads up, a door seems to be open: locking might not work. "


def chiusa_fatto(nome):
    return "Done: %s is locked." % soggetto(nome)


def chiusa_inviato(nome):
    return "I've sent the lock command to %s." % soggetto(nome) + CONFERMA_STATO


FINESTRINI_GIA = "The windows are already closed."
FINESTRINI_FATTO = "Done: windows closed."


def finestrini_inviato(nome):
    return "I've sent the command to close the windows to %s." % soggetto(nome) + CONFERMA_STATO


SPENTO_GIA = "The climate control is already off."
SPENTO_FATTO = "Done: climate control off."


def spento_inviato(nome):
    return "I've sent the command to switch off the climate control to %s." % soggetto(nome) + CONFERMA_STATO


_IMPIANTI = {"clima": "climate control", "caldo": "heating", "freddo": "air conditioning"}


def acceso_fatto(impianto, gradi):
    return "Done: %s on at %d degrees." % (_IMPIANTI[impianto], gradi)


def acceso_inviato(nome, impianto, gradi):
    return "I've sent %s at %d degrees to %s." % (_IMPIANTI[impianto], gradi, soggetto(nome)) + CONFERMA_STATO


TEMP_NON_CAPITA = "I didn't catch the temperature."


def temp_fuori(minimo, massimo):
    return "I can set the climate control between %d and %d degrees." % (minimo, massimo)
