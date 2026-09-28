"""
Test senza rete ne' account: crittografia contro i vettori della libreria di
riferimento (gli stessi di LeapCryptoTest.kt dell'app) e frasi generate da
uno stato reale della T03 (coordinate sostituite con Piazza Maggiore, Bologna).

    python -m pytest test          (oppure: python test/test_offline.py)
"""

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lambda"))

import leapcloud  # noqa: E402
import risposte  # noqa: E402

with open(os.path.join(HERE, "stato_t03.json"), encoding="utf-8") as f:
    STATO = json.load(f)["data"]

ADESSO = STATO["collectTimeMs"] + 10 * 60 * 1000  # dieci minuti dopo il rilevamento


def stato(**modifiche):
    d = copy.deepcopy(STATO)
    d.update(modifiche)
    return risposte.Stato(d)


# ---- Crittografia ---------------------------------------------------------------

def test_password_p12():
    assert leapcloud.derive_account_p12_password("1234567890", "abcdef1234567890") == "q0XbjYhNmBqcyuU"
    assert leapcloud.derive_account_p12_password("987654321012345", "0f8e7d6c5b4a39281706") == "EYa8eGvtSGwRE2d"


def test_hkdf_e_hmac():
    key = leapcloud.derive_sign_key("ikm-test-value", "salt-test-value", "info-test-value")
    assert key.hex() == "dad18471835826bb8ce3e9602b00bf4800d3a5ae3a20066058166fb79c6dc1c4"
    assert leapcloud.hmac_hex(key, "acceptLanguage1deviceid1nonce") == \
        "ad213b135a9d5b7841dad21edafd36fd38ffc1c50bbd021d73f1eab0ef4c911d"


def test_firma_login():
    text = "en-GB1dev1user@example.com01123456pw202602041leapmotor17000000000001.12.3"
    assert leapcloud.sha256_hex(text) == "8e6f8f51f86a6fdef432df332ed970effaa8f8c5c9bfef6ba16c0deda5ae5c4a"


def test_percent_encoding():
    assert leapcloud.q("a b+c/d@e.f~g") == "a%20b%2Bc%2Fd%40e.f~g"
    assert leapcloud.q("Pa$$w0rd!") == "Pa%24%24w0rd%21"


# ---- Frasi ------------------------------------------------------------------------

def test_batteria_ferma():
    assert risposte.frase_batteria(stato()) == \
        "La batteria è all'81 per cento, circa 218 chilometri di autonomia."


def test_batteria_in_carica():
    s = stato(chargeState=2, batteryCurrent=-15.2, chargeRemainTime=130)
    assert risposte.frase_batteria(s).endswith("È in carica e finisce tra circa 2 ore e 10 minuti, all'80 per cento.")


def test_cavo_collegato_al_limite():
    s = stato(chargeState=1, soc=80)
    assert "ha raggiunto il limite impostato" in risposte.frase_batteria(s)


def test_articolo_percentuale():
    assert risposte.al_percento(50) == "al 50 per cento"
    assert risposte.al_percento(81) == "all'81 per cento"
    assert risposte.al_percento(8) == "all'8 per cento"
    assert risposte.al_percento(100) == "al 100 per cento"


def test_tutto_a_posto():
    assert risposte.frase_anomalie(stato()) == \
        "Tutto a posto: l'auto è chiusa a chiave, con finestrini e baule chiusi."


def test_anomalie_multiple():
    s = stato(driverDoorLockStatus=False, rightRearWindowPercent=30, bbcmBackDoorStatus=True)
    assert risposte.frase_anomalie(s) == \
        "Attenzione: c'è un finestrino aperto, il baule è aperto e non è chiusa a chiave."


def test_non_chiusa_ma_in_marcia_non_e_anomalia():
    s = stato(driverDoorLockStatus=False, speed=50)
    assert risposte.anomalie(s) == []


def test_gomma_sgonfia():
    s = stato(leftRearTirePressureState=1)
    assert "la gomma posteriore sinistra ha una pressione anomala" in risposte.frase_anomalie(s)


def test_posizione_indirizzo():
    s = stato()
    ind = {"road": "Piazza Maggiore", "house_number": "1", "city": "Bologna"}
    assert risposte.frase_posizione(s, [], ind) == "L'auto si trova in Piazza Maggiore 1, a Bologna."


def test_posizione_luogo_noto():
    s = stato()
    casa = [{"nome": "a casa", "lat": 44.4940, "lon": 11.3430, "raggio_m": 150}]
    assert risposte.frase_posizione(s, casa, None) == "L'auto è a casa."


def test_eta_dato():
    s = stato()
    assert risposte.nota_eta_dato(s, ADESSO) == ""
    un_giorno_dopo = s.rilevato_ms + 24 * 3600 * 1000
    # collectTimeMs = 12 agosto 2026 09:54:50 UTC (la stringa collectTime del
    # cloud e' in UTC) = 11:54 ora legale italiana
    assert risposte.nota_eta_dato(s, un_giorno_dopo) == "L'ultimo contatto con l'auto è di ieri alle 11 e 54."


def test_ora_solare_e_legale():
    # 15 gennaio 2026 12:00 UTC -> 13:00; 15 luglio 2026 12:00 UTC -> 14:00
    assert risposte.ora_italiana(1768478400000).hour == 13
    assert risposte.ora_italiana(1784116800000).hour == 14


if __name__ == "__main__":
    fallimenti = 0
    for nome, fn in sorted(globals().items()):
        if nome.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok   ", nome)
            except AssertionError as exc:
                fallimenti += 1
                print("FALLITO", nome, exc)
    sys.exit(1 if fallimenti else 0)
