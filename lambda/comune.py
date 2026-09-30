"""
Pezzi condivisi dai moduli delle lingue (lingua_it, lingua_en, lingua_es):
cosa c'e' di anomalo nello stato, detto in modo neutro, e piccole utilita'
di testo. Le frasi vere stanno nei moduli delle lingue.
"""

# Chiavi neutre delle ruote: ogni lingua ha la sua traduzione.
RUOTE = [
    ("ant_sx", "leftFrontTirePressure"),
    ("ant_dx", "rightFrontTirePressure"),
    ("post_sx", "leftRearTirePressure"),
    ("post_dx", "rightRearTirePressure"),
]


def cap(testo):
    return testo[:1].upper() + testo[1:]


def elenco(voci, e):
    """ "a, b e c" con la congiunzione della lingua."""
    return voci[0] if len(voci) == 1 else ", ".join(voci[:-1]) + " " + e + " " + voci[-1]


def cose_aperte(s):
    """Cio' che l'auto "ha" di anomalo: 'portiera', 'finestrino', 'baule', 'gomme'."""
    voci = []
    if s.portiere_aperte:
        voci.append("portiera")
    if s.finestrini_aperti:
        voci.append("finestrino")
    if s.baule_aperto:
        voci.append("baule")
    if s.gomme_anomale:
        voci.append("gomme")
    return voci


def non_chiusa(s):
    # Aperta mentre si guida e' normale: conta solo a veicolo fermo.
    return s.chiusa is False and not s.in_movimento


def durata(minuti, un_ora, ore, un_minuto, minuti_fmt, e):
    h, m = divmod(minuti, 60)
    parti = []
    if h:
        parti.append(un_ora if h == 1 else ore % h)
    if m or not h:
        parti.append(un_minuto if m == 1 else minuti_fmt % m)
    return (" %s " % e).join(parti)
