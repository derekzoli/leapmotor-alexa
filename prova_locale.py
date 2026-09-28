"""
Prova dal PC, con l'account vero, prima di caricare la skill su Amazon.

    python prova_locale.py

Chiede email e password (non le salva da nessuna parte), fa login e lettura
dello stato come fara' la skill, e stampa i tempi e le frasi che Alexa direbbe.
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

vin, car_type = cloud.vehicle
print("\nVeicolo: %s (%s)" % (vin, car_type))
print("Tempi: login %.1f s | primo stato %.1f s | stato con sessione gia' aperta %.1f s"
      % (t1 - t0, t2 - t1, t3 - t2))
print("Alexa concede circa 8 secondi: il caso peggiore (container a freddo) e' login + primo stato = %.1f s"
      % (t2 - t0))

with open(os.path.join(HERE, "ultimo_stato.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

s = risposte.Stato(data)
luoghi = cfg.get("luoghi") or []
indirizzo = None
if s.lat is not None and not risposte.luogo_noto(s, luoghi):
    indirizzo = posizione.indirizzo(s.lat, s.lon)

print("\n--- Cosa direbbe Alexa ---")
print("Carica:    ", risposte.con_eta(risposte.frase_batteria(s), s))
print("Posizione: ", risposte.con_eta(risposte.frase_posizione(s, luoghi, indirizzo), s))
print("Anomalie:  ", risposte.con_eta(risposte.frase_anomalie(s), s))
if s.lat is not None:
    print("\nMappa:", posizione.link_mappa(s.lat, s.lon))
    print("Coordinate per config.json (luoghi): \"lat\": %.6f, \"lon\": %.6f" % (s.lat, s.lon))
print("\nStato grezzo salvato in ultimo_stato.json")
