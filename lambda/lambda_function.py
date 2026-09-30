"""
Skill Alexa "mia lippina" (MyLeapCar): stato e comandi della Leapmotor.

Domande: carica, posizione, anomalie, riepilogo.
Comandi (solo con "comandi": true e il PIN in config.json): chiudere l'auto,
chiudere i finestrini, accendere e spegnere il clima. Aprire l'auto o i
finestrini NON e' previsto: una skill vocale la puo' usare chiunque sia nella
stanza, compresa la TV.
"""

import json
import logging
import os
import time
from xml.sax.saxutils import escape

from ask_sdk_core.dispatch_components import AbstractExceptionHandler, AbstractRequestHandler
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_model.ui import SimpleCard

import comandi
import posizione
import risposte
from leapcloud import LeapCloud, LeapError

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

TITOLO = "MyLeapCar"

# Alexa aspetta circa 8 secondi in tutto: oltre questo margine dall'inizio
# della richiesta si smette di attendere la conferma dell'auto.
ATTESA_CONFERMA_S = 6.0

AIUTO = ("Puoi chiedermi quanto è carica l'auto, dove si trova, "
         "oppure se è tutto a posto. Posso anche chiuderla, chiudere i finestrini "
         "e accendere o spegnere il clima. Cosa vuoi fare?")

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

NON_CONFIGURATA = ("La skill non è ancora configurata: inserisci email e password "
                   "dell'account Leapmotor nel file config punto json.")


def _carica_config():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    email = (cfg.get("email") or "").strip()
    if not email or "@" not in email or email.startswith("INSERISCI"):
        return None
    return cfg


CONFIG = _carica_config()

# Vive quanto il container Lambda: le richieste ravvicinate riusano la sessione
# invece di rifare il login ogni volta.
CLOUD = LeapCloud(CONFIG["email"], CONFIG["password"]) if CONFIG else None


def _vin():
    return (CONFIG.get("vin") or "").strip() or None


def _stato():
    inizio = time.time()
    data = CLOUD.raw_status(_vin())
    log.info("stato letto in %.1f s", time.time() - inizio)
    return risposte.Stato(data)


def _nome():
    """Nome dell'auto da pronunciare: `nome` in config.json, altrimenti quello dell'app."""
    nome = ((CONFIG or {}).get("nome") or "").strip()
    if not nome and CLOUD is not None and CLOUD.vehicle is not None:
        nome = CLOUD.vehicle.nickname
    return risposte.nome_parlato(nome)


def _titolo():
    return _nome() or TITOLO


def _fine(handler_input, testo, scheda=None):
    # speak() finisce dentro <speak>: un & in un nome di via romperebbe l'SSML.
    return (handler_input.response_builder
            .speak(escape(testo))
            .set_card(SimpleCard(_titolo(), scheda or testo))
            .set_should_end_session(True)
            .response)


def _rispondi(handler_input, domanda):
    """domanda: 'batteria', 'posizione', 'anomalie' o 'riepilogo'."""
    if CLOUD is None:
        return _fine(handler_input, NON_CONFIGURATA)
    try:
        s = _stato()
    except LeapError as exc:
        log.warning("errore Leapmotor: %s", exc)
        return _fine(handler_input, ERRORI.get(exc.kind, ERRORI["server"]))

    luoghi = CONFIG.get("luoghi") or []
    indirizzo = None
    if domanda in ("posizione", "riepilogo") and s.lat is not None and not risposte.luogo_noto(s, luoghi):
        indirizzo = posizione.indirizzo(s.lat, s.lon)

    if domanda == "batteria":
        testo = risposte.frase_batteria(s, _nome())
    elif domanda == "posizione":
        testo = risposte.frase_posizione(s, luoghi, indirizzo, _nome())
    elif domanda == "anomalie":
        testo = risposte.frase_anomalie(s, _nome())
    else:
        testo = risposte.frase_riepilogo(s, luoghi, indirizzo, _nome())
    testo = risposte.con_eta(testo, s)

    scheda = testo
    if domanda in ("posizione", "riepilogo") and s.lat is not None:
        scheda += "\n\nMappa: " + posizione.link_mappa(s.lat, s.lon)
    return _fine(handler_input, testo, scheda)


def _esegui(handler_input, azione, temperatura=None):
    """azione: vedi comandi.pianifica."""
    inizio = time.time()
    if CLOUD is None:
        return _fine(handler_input, NON_CONFIGURATA)
    if CONFIG.get("comandi") is not True:
        return _fine(handler_input, "I comandi sono disattivati nella configurazione della skill.")
    pin = str(CONFIG.get("pin") or "").strip()
    if not pin:
        return _fine(handler_input, "Per i comandi serve il PIN del veicolo nel file di configurazione.")

    try:
        s = _stato()  # serve comunque: niente comandi inutili, niente chiusura in marcia
        piano = comandi.pianifica(
            azione, s, CLOUD.vehicle.is_t03, temperatura,
            ventola=CONFIG.get("ventola") or comandi.VENTOLA_PREDEFINITA,
            nome=_nome(),
        )
        if piano.risposta:
            return _fine(handler_input, piano.risposta)
        confermato = CLOUD.comando(pin, piano.cmd_id, piano.contenuto,
                                   scadenza=inizio + ATTESA_CONFERMA_S, wanted_vin=_vin())
    except LeapError as exc:
        log.warning("errore Leapmotor (%s): %s", azione, exc)
        return _fine(handler_input, ERRORI.get(exc.kind, ERRORI["server"]))

    log.info("comando %s %s in %.1f s", azione, "confermato" if confermato else "inviato",
             time.time() - inizio)
    return _fine(handler_input, piano.fatto if confermato else piano.inviato)


def _slot(handler_input, nome):
    slots = handler_input.request_envelope.request.intent.slots or {}
    slot = slots.get(nome)
    return slot.value if slot is not None else None


class Apertura(AbstractRequestHandler):
    """"Alexa, apri mia lippina": riepilogo completo e chiude."""

    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        return _rispondi(handler_input, "riepilogo")


class Domanda(AbstractRequestHandler):
    INTENT = {
        "BatteriaIntent": "batteria",
        "PosizioneIntent": "posizione",
        "AnomalieIntent": "anomalie",
        "RiepilogoIntent": "riepilogo",
    }

    def can_handle(self, handler_input):
        return any(is_intent_name(n)(handler_input) for n in self.INTENT)

    def handle(self, handler_input):
        nome = handler_input.request_envelope.request.intent.name
        return _rispondi(handler_input, self.INTENT[nome])


class Comando(AbstractRequestHandler):
    INTENT = {
        "ChiudiAutoIntent": "chiudi",
        "ChiudiFinestriniIntent": "finestrini",
        "ClimaIntent": "clima",
        "RiscaldamentoIntent": "caldo",
        "RaffreddamentoIntent": "freddo",
        "SpegniClimaIntent": "spegni",
    }

    def can_handle(self, handler_input):
        return any(is_intent_name(n)(handler_input) for n in self.INTENT)

    def handle(self, handler_input):
        nome = handler_input.request_envelope.request.intent.name
        azione = self.INTENT[nome]
        temperatura = _slot(handler_input, "temperatura") if azione in ("clima", "caldo", "freddo") else None
        return _esegui(handler_input, azione, temperatura)


class Aiuto(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.HelpIntent")(handler_input)
                or is_intent_name("AMAZON.FallbackIntent")(handler_input)
                or is_intent_name("AMAZON.NavigateHomeIntent")(handler_input))

    def handle(self, handler_input):
        return handler_input.response_builder.speak(AIUTO).ask(AIUTO).response


class Fine(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input)
                or is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        return handler_input.response_builder.speak("Ciao!").set_should_end_session(True).response


class FineSessione(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


class Imprevisto(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        log.error(exception, exc_info=True)
        testo = "Qualcosa è andato storto mentre interrogavo l'auto. Riprova tra poco."
        return handler_input.response_builder.speak(testo).set_should_end_session(True).response


sb = SkillBuilder()
sb.add_request_handler(Apertura())
sb.add_request_handler(Domanda())
sb.add_request_handler(Comando())
sb.add_request_handler(Aiuto())
sb.add_request_handler(Fine())
sb.add_request_handler(FineSessione())
sb.add_exception_handler(Imprevisto())

lambda_handler = sb.lambda_handler()
