"""Crea leapmotor-alexa-lambda.zip da importare nella scheda Code della console Alexa."""

import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SORGENTE = os.path.join(HERE, "lambda")
DESTINAZIONE = os.path.join(HERE, "leapmotor-alexa-lambda.zip")

# Controllo senza importare leapcloud: per creare lo zip non servono le librerie.
CERTIFICATI = [("app.crt", "app.key"), ("app_crt.pem", "app_key.pem")]
if not any(os.path.isfile(os.path.join(SORGENTE, c)) and os.path.isfile(os.path.join(SORGENTE, k))
           for c, k in CERTIFICATI):
    sys.exit("Mancano i certificati: scarica app.crt e app.key da "
             "https://github.com/markoceri/leapmotor-certs e mettili nella cartella lambda.")

with zipfile.ZipFile(DESTINAZIONE, "w", zipfile.ZIP_DEFLATED) as z:
    for nome in sorted(os.listdir(SORGENTE)):
        percorso = os.path.join(SORGENTE, nome)
        if os.path.isfile(percorso) and not nome.endswith(".pyc"):
            # La console vuole i file dentro una cartella lambda/ alla radice dello zip.
            z.write(percorso, "lambda/" + nome)
            print("  + lambda/" + nome)
print("Creato", DESTINAZIONE)
