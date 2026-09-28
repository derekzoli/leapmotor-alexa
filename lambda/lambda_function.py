"""
Skill Alexa "mia lippina" (MyLeapCar): carica, posizione e anomalie della Leapmotor.

Solo lettura: la skill non conosce il PIN del veicolo, quindi non puo'
inviare comandi all'auto.
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

import posizione
import risposte
from leapcloud import LeapCloud, LeapError

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

TITOLO = "MyLeapCar"

AIUTO = ("Puoi chiedermi quanto è carica l'auto, dove si trova, "
         "oppure se ci sono anomalie, come finestrini aperti o l'auto non chiusa. "
         "Cosa vuoi sapere?")

ERRORI = {
    "rete": "Il cloud Leapmotor non risponde in questo momento. Riprova tra poco.",
    "credenziali": ("Non riesco ad accedere all'account Leapmotor. "
                    "Controlla email e password nel file di configurazione della skill."),
    "certificati_app": ("Mancano i certificati dell'app Leapmotor nella cartella lambda. "
                        "Trovi le istruzioni nella pagina del progetto."),
    "certificato": "Il cloud Leapmotor ha mandato un certificato che non riesco ad aprire.",
    "sessione": "La sessione con il cloud Leapmotor è scaduta. Riprova.",
    "server": "Il cloud Leapmotor ha risposto con un errore. Riprova tra poco.",
}


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


def _stato():
    inizio = time.time()
    data = CLOUD.raw_status((CONFIG.get("vin") or "").strip() or None)
    log.info("stato letto in %.1f s", time.time() - inizio)
    return risposte.Stato(data)


def _rispondi(handler_input, domanda):
    """domanda: 'batteria', 'posizione', 'anomalie' o 'riepilogo'."""
    rb = handler_input.response_builder
    if CLOUD is None:
        testo = ("La skill non è ancora configurata: inserisci email e password "
                 "dell'account Leapmotor nel file config punto json.")
        return rb.speak(testo).set_card(SimpleCard(TITOLO, testo)).set_should_end_session(True).response

    try:
        s = _stato()
    except LeapError as exc:
        log.warning("errore Leapmotor: %s", exc)
        testo = ERRORI.get(exc.kind, ERRORI["server"])
        return rb.speak(testo).set_card(SimpleCard(TITOLO, testo)).set_should_end_session(True).response

    luoghi = CONFIG.get("luoghi") or []
    indirizzo = None
    if domanda in ("posizione", "riepilogo") and s.lat is not None and not risposte.luogo_noto(s, luoghi):
        indirizzo = posizione.indirizzo(s.lat, s.lon)

    if domanda == "batteria":
        testo = risposte.frase_batteria(s)
    elif domanda == "posizione":
        testo = risposte.frase_posizione(s, luoghi, indirizzo)
    elif domanda == "anomalie":
        testo = risposte.frase_anomalie(s)
    else:
        testo = risposte.frase_riepilogo(s, luoghi, indirizzo)
    testo = risposte.con_eta(testo, s)

    scheda = testo
    if domanda in ("posizione", "riepilogo") and s.lat is not None:
        scheda += "\n\nMappa: " + posizione.link_mappa(s.lat, s.lon)

    # speak() finisce dentro <speak>: un & in un nome di via romperebbe l'SSML.
    return rb.speak(escape(testo)).set_card(SimpleCard(TITOLO, scheda)).set_should_end_session(True).response


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
sb.add_request_handler(Aiuto())
sb.add_request_handler(Fine())
sb.add_request_handler(FineSessione())
sb.add_exception_handler(Imprevisto())

lambda_handler = sb.lambda_handler()
