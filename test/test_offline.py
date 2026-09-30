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

import comandi  # noqa: E402
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
        "Attenzione: l'auto ha un finestrino aperto e il baule aperto, e non è chiusa a chiave."


def test_non_chiusa_ma_in_marcia_non_e_anomalia():
    s = stato(driverDoorLockStatus=False, speed=50)
    assert risposte.anomalie(s) == []


def test_gomma_sgonfia():
    s = stato(leftRearTirePressureState=1)
    assert risposte.frase_anomalie(s) == \
        "Attenzione: l'auto ha una pressione anomala sulla gomma posteriore sinistra."


def test_posizione_indirizzo():
    s = stato()
    ind = {"road": "Piazza Maggiore", "house_number": "1", "city": "Bologna"}
    assert risposte.frase_posizione(s, [], ind) == "L'auto si trova in Piazza Maggiore 1, a Bologna."


def test_posizione_luogo_noto():
    s = stato()
    casa = [{"nome": "a casa", "lat": 44.4940, "lon": 11.3430, "raggio_m": 150}]
    assert risposte.frase_posizione(s, casa, None) == "L'auto è a casa."


def test_nome_auto():
    assert risposte.nome_parlato("ElettraLamborghini") == "Elettra Lamborghini"
    assert risposte.nome_parlato("  ") is None
    ind = {"road": "Piazza Maggiore", "house_number": "1", "city": "Bologna"}
    assert risposte.frase_posizione(stato(), [], ind, "Elettra Lamborghini") == \
        "Elettra Lamborghini si trova in Piazza Maggiore 1, a Bologna."
    assert risposte.frase_riepilogo(stato(), [], ind, "Elettra Lamborghini").startswith(
        "Elettra Lamborghini si trova in Piazza Maggiore 1, a Bologna. La batteria è all'81 per cento")


def test_nome_in_tutte_le_risposte():
    n = "Elettra Lamborghini"
    assert risposte.frase_anomalie(stato(), n) == \
        "Tutto a posto: Elettra Lamborghini è chiusa a chiave, con finestrini e baule chiusi."
    assert risposte.frase_anomalie(stato(driverDoorLockStatus=False), n) == \
        "Attenzione: Elettra Lamborghini non è chiusa a chiave."
    assert risposte.frase_batteria(stato(), n) == \
        "Elettra Lamborghini è carica all'81 per cento, con circa 218 chilometri di autonomia."
    riepilogo = risposte.frase_riepilogo(stato(), [], None, n)
    assert riepilogo.count(n) == 1 and "Tutto a posto: è chiusa a chiave" in riepilogo
    assert comandi.pianifica("chiudi", stato(), True, nome=n).risposta == "Elettra Lamborghini è già chiusa a chiave."
    p = comandi.pianifica("caldo", stato(), True, "22", nome=n)
    assert p.inviato.startswith("Ho mandato a Elettra Lamborghini: riscaldamento a 22 gradi.")
    assert comandi.pianifica("finestrini", stato(leftRearWindowPercent=5), True, nome="Alba").inviato \
        .startswith("Ho mandato ad Alba la chiusura dei finestrini.")


def test_posizione_senza_indirizzo_in_movimento():
    assert risposte.frase_posizione(stato(speed=50), [], None) == (
        "Non riesco a ricavare l'indirizzo dell'auto, ma trovi la posizione nella scheda dell'app Alexa. "
        "L'auto è in movimento.")


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


# ---- Comandi ------------------------------------------------------------------------

SPENTO_T03 = ('{"circle":"out","mode":"wind","operate":"off","position":"all",'
              '"temperature":"26","windlevel":"3","wshld":"0"}')


def test_chiudi_gia_chiusa():
    assert comandi.pianifica("chiudi", stato(), True).risposta == "L'auto è già chiusa a chiave."


def test_chiudi_aperta():
    p = comandi.pianifica("chiudi", stato(driverDoorLockStatus=False), True)
    assert (p.cmd_id, p.contenuto) == ("110", '{"value":"lock"}')
    assert p.fatto == "Fatto: l'auto è chiusa a chiave."


def test_chiudi_in_marcia_no():
    p = comandi.pianifica("chiudi", stato(driverDoorLockStatus=False, speed=40), True)
    assert p.cmd_id is None and "movimento" in p.risposta


def test_finestrini():
    assert comandi.pianifica("finestrini", stato(), True).risposta == "I finestrini sono già chiusi."
    p = comandi.pianifica("finestrini", stato(leftRearWindowPercent=40), True)
    assert (p.cmd_id, p.contenuto) == ("230", '{"value":"0"}')


def test_spegni_clima_t03():
    assert comandi.pianifica("spegni", stato(), True).risposta == "Il clima è già spento."
    p = comandi.pianifica("spegni", stato(acSwitch=True), True)
    # Lo stesso payload che la T03 esegue davvero (verificato sull'auto il 6 agosto 2026).
    assert (p.cmd_id, p.contenuto) == ("170", SPENTO_T03)
    assert comandi.pianifica("spegni", stato(acSwitch=True), False).contenuto == '{"operate":"off"}'


def test_riscaldamento():
    p = comandi.pianifica("caldo", stato(), True, "22")
    assert p.contenuto == ('{"circle":"out","mode":"hot","operate":"manual","position":"all",'
                           '"temperature":"22","windlevel":"3","wshld":"0"}')
    assert p.fatto == "Fatto: riscaldamento acceso a 22 gradi."


def test_clima_sceglie_dalla_temperatura_esterna():
    estate = comandi.pianifica("clima", stato(outdoorTemp=35), True, "22")
    inverno = comandi.pianifica("clima", stato(outdoorTemp=4), True, "22")
    assert '"mode":"cold"' in estate.contenuto and estate.fatto == "Fatto: aria condizionata accesa a 22 gradi."
    assert '"mode":"hot"' in inverno.contenuto


def test_clima_altri_modelli_automatico():
    p = comandi.pianifica("clima", stato(), False, "21")
    assert '"mode":"nohotcold","operate":"auto"' in p.contenuto


def test_temperatura_predefinita_e_limiti():
    assert '"temperature":"22"' in comandi.pianifica("freddo", stato(), True, None).contenuto
    assert comandi.pianifica("caldo", stato(), True, "35").risposta == "Posso impostare il clima tra 18 e 32 gradi."
    assert comandi.pianifica("caldo", stato(), True, "?").cmd_id == "170"


def test_stato_dice_clima_acceso():
    assert risposte.frase_anomalie(stato(acSwitch=True, acSetting=21)).endswith("Il clima è acceso a 21 gradi.")
    assert "clima" not in risposte.frase_anomalie(stato())


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
