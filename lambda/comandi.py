"""
Cosa mandare all'auto e cosa rispondere, per ogni comando vocale.

Nessuna rete qui dentro: si decide a partire dallo stato gia' letto, cosi'
si prova offline. Volutamente NON ci sono l'apertura dell'auto ne' quella
dei finestrini: una skill vocale la puo' usare chiunque sia nella stanza.
"""

CMD_LOCK = "110"
CMD_CLIMATE = "170"
CMD_WINDOWS = "230"

TEMP_MIN = 18
TEMP_MAX = 32
TEMP_PREDEFINITA = 22
VENTOLA_PREDEFINITA = 3

CONFERMA_STATO = " Tra un minuto chiedimi se è tutto a posto per la conferma."


def _chi(nome):
    return nome or "l'auto"


def _a_chi(nome):
    if not nome:
        return "all'auto"
    return ("ad " if nome[:1].lower() == "a" else "a ") + nome


def _cap(testo):
    return testo[:1].upper() + testo[1:]


class Piano:
    """
    `risposta` da sola: niente da mandare (gia' fatto, non possibile...).
    Altrimenti `cmd_id` + `contenuto` da inviare, e le due frasi per quando
    l'auto conferma (`fatto`) o non fa in tempo a confermare (`inviato`).
    """

    def __init__(self, risposta=None, cmd_id=None, contenuto=None, fatto=None, inviato=None):
        self.risposta = risposta
        self.cmd_id = cmd_id
        self.contenuto = contenuto
        self.fatto = fatto
        self.inviato = inviato


def payload_clima(circle, mode, operate, temperatura, ventola):
    # Stringa scritta a mano: entra nella firma, quindi ordine delle chiavi e
    # assenza di spazi devono restare identici a quelli dell'app.
    return ('{"circle":"%s","mode":"%s","operate":"%s","position":"all",'
            '"temperature":"%d","windlevel":"%d","wshld":"0"}'
            % (circle, mode, operate, temperatura, ventola))


def payload_spegni(is_t03):
    """
    T03: `operate=off` dentro il payload COMPLETO (verificato sull'auto, accolto
    anche in leapmotor-mate 3.10.0). Gli altri modelli vogliono il comando nudo.
    """
    if is_t03:
        return payload_clima("out", "wind", "off", 26, 3)
    return '{"operate":"off"}'


def _temperatura(valore, s):
    """(gradi, errore): errore e' la frase da dire se il numero non va bene."""
    if valore in (None, "", "?"):
        return TEMP_PREDEFINITA, None
    try:
        gradi = int(round(float(str(valore).replace(",", "."))))
    except ValueError:
        return None, "Non ho capito la temperatura."
    if gradi < TEMP_MIN or gradi > TEMP_MAX:
        return None, "Posso impostare il clima tra %d e %d gradi." % (TEMP_MIN, TEMP_MAX)
    return gradi, None


def pianifica(azione, s, is_t03, temperatura=None, ventola=VENTOLA_PREDEFINITA, nome=None):
    """
    azione: 'chiudi', 'finestrini', 'clima', 'caldo', 'freddo', 'spegni'.
    nome: come chiamare l'auto nelle risposte ("Elettra Lamborghini"); None = "l'auto".
    """
    chi, a_chi = _chi(nome), _a_chi(nome)
    if azione == "chiudi":
        if s.in_movimento:
            return Piano("%s è in movimento: non la chiudo a distanza." % _cap(chi))
        if s.chiusa:
            return Piano("%s è già chiusa a chiave." % _cap(chi))
        avviso = "Attenzione, risulta una portiera aperta: la chiusura potrebbe non riuscire. " \
            if s.portiere_aperte else ""
        return Piano(
            cmd_id=CMD_LOCK, contenuto='{"value":"lock"}',
            fatto=avviso + "Fatto: %s è chiusa a chiave." % chi,
            inviato=avviso + "Ho mandato %s il comando di chiusura." % a_chi + CONFERMA_STATO,
        )

    if azione == "finestrini":
        if not s.finestrini_aperti:
            return Piano("I finestrini sono già chiusi.")
        return Piano(
            cmd_id=CMD_WINDOWS, contenuto='{"value":"0"}',
            fatto="Fatto: finestrini chiusi.",
            inviato="Ho mandato %s la chiusura dei finestrini." % a_chi + CONFERMA_STATO,
        )

    if azione == "spegni":
        if s.clima_acceso is False:
            return Piano("Il clima è già spento.")
        return Piano(
            cmd_id=CMD_CLIMATE, contenuto=payload_spegni(is_t03),
            fatto="Fatto: clima spento.",
            inviato="Ho mandato %s lo spegnimento del clima." % a_chi + CONFERMA_STATO,
        )

    if azione in ("clima", "caldo", "freddo"):
        gradi, errore = _temperatura(temperatura, s)
        if errore:
            return Piano(errore)
        ventola = max(1, min(7, int(ventola or VENTOLA_PREDEFINITA)))
        if azione == "clima":
            # "Accendi il clima" senza dire caldo o freddo: decide la temperatura esterna.
            caldo = s.temp_esterna is not None and gradi > s.temp_esterna
        else:
            caldo = azione == "caldo"
        if azione == "clima" and not is_t03:
            # Gli altri modelli hanno un vero automatico; la T03 lo ignora
            # in silenzio (leapmotor-mate #67), quindi li' si sceglie noi.
            contenuto = payload_clima("out", "nohotcold", "auto", gradi, ventola)
            impianto = "clima"
        else:
            contenuto = payload_clima("out", "hot" if caldo else "cold", "manual", gradi, ventola)
            impianto = "riscaldamento" if caldo else "aria condizionata"
        acceso = "accesa" if impianto == "aria condizionata" else "acceso"
        return Piano(
            cmd_id=CMD_CLIMATE, contenuto=contenuto,
            fatto="Fatto: %s %s a %d gradi." % (impianto, acceso, gradi),
            inviato="Ho mandato %s: %s a %d gradi." % (a_chi, impianto, gradi) + CONFERMA_STATO,
        )

    raise ValueError("azione sconosciuta: %s" % azione)
