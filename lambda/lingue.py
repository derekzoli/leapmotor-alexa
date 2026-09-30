"""Dalla lingua della richiesta Alexa ("it-IT", "en-GB", "es-ES"…) al modulo delle frasi."""

import lingua_en
import lingua_es
import lingua_it

_MODULI = {"it": lingua_it, "en": lingua_en, "es": lingua_es}


def get(locale):
    """Qualsiasi variante (en-US, es-MX…) usa la sua lingua; sconosciute -> italiano."""
    return _MODULI.get((locale or "it")[:2].lower(), lingua_it)
