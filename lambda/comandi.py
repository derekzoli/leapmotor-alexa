"""
Cosa mandare all'auto e cosa rispondere, per ogni comando vocale.

Nessuna rete qui dentro: si decide a partire dallo stato gia' letto, cosi'
si prova offline. Volutamente NON ci sono l'apertura dell'auto ne' quella
dei finestrini: una skill vocale la puo' usare chiunque sia nella stanza.
"""

import lingue

CMD_LOCK = "110"
CMD_CLIMATE = "170"
CMD_WINDOWS = "230"

TEMP_MIN = 18
TEMP_MAX = 32
TEMP_PREDEFINITA = 22
VENTOLA_PREDEFINITA = 3


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


def _temperatura(valore, L):
    """(gradi, errore): errore e' la frase da dire se il numero non va bene."""
    if valore in (None, "", "?"):
        return TEMP_PREDEFINITA, None
    try:
        gradi = int(round(float(str(valore).replace(",", "."))))
    except ValueError:
        return None, L.TEMP_NON_CAPITA
    if gradi < TEMP_MIN or gradi > TEMP_MAX:
        return None, L.temp_fuori(TEMP_MIN, TEMP_MAX)
    return gradi, None


def pianifica(azione, s, is_t03, temperatura=None, ventola=VENTOLA_PREDEFINITA, nome=None, lingua="it"):
    """
    azione: 'chiudi', 'finestrini', 'clima', 'caldo', 'freddo', 'spegni'.
    nome: come chiamare l'auto nelle risposte ("Elettra Lamborghini"); None = "l'auto".
    lingua: "it", "en", "es" (o il locale di Alexa, "en-GB"…).
    """
    L = lingue.get(lingua)
    if azione == "chiudi":
        if s.in_movimento:
            return Piano(L.in_movimento(nome))
        if s.chiusa:
            return Piano(L.gia_chiusa(nome))
        avviso = L.AVVISO_PORTIERA if s.portiere_aperte else ""
        return Piano(
            cmd_id=CMD_LOCK, contenuto='{"value":"lock"}',
            fatto=avviso + L.chiusa_fatto(nome),
            inviato=avviso + L.chiusa_inviato(nome),
        )

    if azione == "finestrini":
        if not s.finestrini_aperti:
            return Piano(L.FINESTRINI_GIA)
        return Piano(
            cmd_id=CMD_WINDOWS, contenuto='{"value":"0"}',
            fatto=L.FINESTRINI_FATTO,
            inviato=L.finestrini_inviato(nome),
        )

    if azione == "spegni":
        if s.clima_acceso is False:
            return Piano(L.SPENTO_GIA)
        return Piano(
            cmd_id=CMD_CLIMATE, contenuto=payload_spegni(is_t03),
            fatto=L.SPENTO_FATTO,
            inviato=L.spento_inviato(nome),
        )

    if azione in ("clima", "caldo", "freddo"):
        gradi, errore = _temperatura(temperatura, L)
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
            impianto = "caldo" if caldo else "freddo"
        return Piano(
            cmd_id=CMD_CLIMATE, contenuto=contenuto,
            fatto=L.acceso_fatto(impianto, gradi),
            inviato=L.acceso_inviato(nome, impianto, gradi),
        )

    raise ValueError("azione sconosciuta: %s" % azione)
