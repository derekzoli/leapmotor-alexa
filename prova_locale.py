"""
Prova dal PC, con l'account vero, prima di caricare la skill su Amazon.

    python prova_locale.py

Chiede email e password (non le salva da nessuna parte), fa login e lettura
dello stato come fara' la skill, e stampa i tempi e le frasi che Alexa direbbe.
Non invia comandi all'auto: quelli si provano direttamente con Alexa.
"""

import getpass
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lambda"))

try:
    # Norton intercetta l'HTTPS verso OpenStreetMap: con truststore Python usa
    # i certificati di Windows, che conoscono Norton. Su Amazon non serve.
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

import posizione  # noqa: E402
import risposte  # noqa: E402
from leapcloud import LeapCloud, LeapError  # noqa: E402

with open(os.path.join(HERE, "lambda", "config.json"), encoding="utf-8") as f:
    cfg = json.load(f)

email = input("Email del terzo account Leapmotor: ").strip()
password = getpass.getpass("Password (non si vede mentre scrivi): ")

cloud = LeapCloud(email, password)
try:
    t0 = time.time()
    cloud.login()
    t1 = time.time()
    data = cloud.raw_status((cfg.get("vin") or "").strip() or None)
    t2 = time.time()
    data2 = cloud.raw_status((cfg.get("vin") or "").strip() or None)
    t3 = time.time()
except LeapError as exc:
    print("\nERRORE (%s): %s" % (exc.kind, exc.detail))
    if exc.kind == "credenziali":
        print("Email o password non accettate dal cloud Leapmotor.")
    sys.exit(1)

v = cloud.vehicle
print("\nVeicolo: %s (%s)" % (v.vin, v.car_type))
print("Nickname visto da questo account: %s" % (v.nickname or "(nessuno)"))
with open(os.path.join(HERE, "ultimo_elenco_veicoli.json"), "w", encoding="utf-8") as f:
    json.dump(cloud.ultimo_elenco, f, ensure_ascii=False, indent=2)
print("Elenco veicoli completo salvato in ultimo_elenco_veicoli.json")
print("Comandi concessi dal cloud: %s" % (", ".join(v.rights) or "(elenco non fornito)"))
for cmd, cosa in (("110", "chiudere l'auto"), ("230", "finestrini"), ("170", "clima")):
    print("  %s %s" % ("si'" if v.consente(cmd) else "NO ", cosa))
print("Tempi: login %.1f s | primo stato %.1f s | stato con sessione gia' aperta %.1f s"
      % (t1 - t0, t2 - t1, t3 - t2))
print("Alexa concede circa 8 secondi: il caso peggiore (container a freddo) e' login + primo stato = %.1f s"
      % (t2 - t0))

with open(os.path.join(HERE, "ultimo_stato.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

s = risposte.Stato(data)
luoghi = cfg.get("luoghi") or []
nome = risposte.nome_parlato(cfg.get("nome") or v.nickname)
fuso = int(cfg.get("fuso_orario", 1))

for lingua, titolo in (("it", "italiano"), ("en", "inglese"), ("es", "spagnolo")):
    indirizzo = None
    if s.lat is not None and not risposte.luogo_noto(s, luoghi, lingua):
        indirizzo = posizione.indirizzo(s.lat, s.lon, lingua)
    print("\n--- Cosa direbbe Alexa in %s ---" % titolo)
    print("Carica:    ", risposte.con_eta(risposte.frase_batteria(s, nome, lingua), s, lingua=lingua, fuso_ore=fuso))
    print("Posizione: ", risposte.con_eta(risposte.frase_posizione(s, luoghi, indirizzo, nome, lingua), s,
                                          lingua=lingua, fuso_ore=fuso))
    print("Anomalie:  ", risposte.con_eta(risposte.frase_anomalie(s, nome, lingua=lingua), s,
                                          lingua=lingua, fuso_ore=fuso))
if s.lat is not None:
    print("\nMappa:", posizione.link_mappa(s.lat, s.lon))
    print("Coordinate per config.json (luoghi): \"lat\": %.6f, \"lon\": %.6f" % (s.lat, s.lon))
print("\nStato grezzo salvato in ultimo_stato.json")
