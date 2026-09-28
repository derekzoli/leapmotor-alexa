"""
Client minimo del cloud Leapmotor, in SOLA LETTURA.

Porting del sottoinsieme che serve alla skill (login, elenco veicoli, stato)
dall'app MyLeapCar (LeapCrypto.kt / LeapClient.kt), a sua volta portata da
markoceri/leapmotor-api. Nessun comando remoto: la skill non conosce il PIN
del veicolo e quindi non puo' aprire, chiudere o accendere nulla.

MD5, SM4 con round key fisse e la mancata verifica del certificato server
sono imposti dal protocollo, non sono scelte di sicurezza di questo codice.
"""

import base64
import hashlib
import hmac
import json
import os
import random
import tempfile
import time
import uuid
from urllib.parse import quote

import requests
import urllib3
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://appgateway.leapmotor-international.de"
APP_VERSION = "1.12.3"
SOURCE = "leapmotor"
CHANNEL = "1"
LANGUAGE = "en-GB"
DEVICE_TYPE = "1"
P12_ENC_ALG = "1"
POLICY_ID = "20260204"

# (connessione, lettura) in secondi: Alexa concede circa 8 secondi in tutto,
# meglio una risposta "il cloud non risponde" che un silenzio.
TIMEOUT = (3, 6)

HERE = os.path.dirname(os.path.abspath(__file__))

# I certificati dell'app non sono nel repository: si scaricano da
# https://github.com/markoceri/leapmotor-certs (app.crt / app.key) e si mettono
# accanto a questo file. Vanno bene anche i nomi app_crt.pem / app_key.pem.
_CERT_NOMI = [("app.crt", "app.key"), ("app_crt.pem", "app_key.pem")]


def app_cert():
    for crt, key in _CERT_NOMI:
        coppia = (os.path.join(HERE, crt), os.path.join(HERE, key))
        if os.path.isfile(coppia[0]) and os.path.isfile(coppia[1]):
            return coppia
    return None


class LeapError(Exception):
    """kind: 'rete', 'credenziali', 'certificati_app', 'certificato', 'sessione', 'server'."""

    def __init__(self, kind, detail):
        super().__init__("%s: %s" % (kind, detail))
        self.kind = kind
        self.detail = detail


# ---- SM4 (solo per la password del PKCS#12 dell'account) -----------------------

_SBOX = [
    0xD6, 0x90, 0xE9, 0xFE, 0xCC, 0xE1, 0x3D, 0xB7, 0x16, 0xB6, 0x14, 0xC2, 0x28, 0xFB, 0x2C, 0x05,
    0x2B, 0x67, 0x9A, 0x76, 0x2A, 0xBE, 0x04, 0xC3, 0xAA, 0x44, 0x13, 0x26, 0x49, 0x86, 0x06, 0x99,
    0x9C, 0x42, 0x50, 0xF4, 0x91, 0xEF, 0x98, 0x7A, 0x33, 0x54, 0x0B, 0x43, 0xED, 0xCF, 0xAC, 0x62,
    0xE4, 0xB3, 0x1C, 0xA9, 0xC9, 0x08, 0xE8, 0x95, 0x80, 0xDF, 0x94, 0xFA, 0x75, 0x8F, 0x3F, 0xA6,
    0x47, 0x07, 0xA7, 0xFC, 0xF3, 0x73, 0x17, 0xBA, 0x83, 0x59, 0x3C, 0x19, 0xE6, 0x85, 0x4F, 0xA8,
    0x68, 0x6B, 0x81, 0xB2, 0x71, 0x64, 0xDA, 0x8B, 0xF8, 0xEB, 0x0F, 0x4B, 0x70, 0x56, 0x9D, 0x35,
    0x1E, 0x24, 0x0E, 0x5E, 0x63, 0x58, 0xD1, 0xA2, 0x25, 0x22, 0x7C, 0x3B, 0x01, 0x21, 0x78, 0x87,
    0xD4, 0x00, 0x46, 0x57, 0x9F, 0xD3, 0x27, 0x52, 0x4C, 0x36, 0x02, 0xE7, 0xA0, 0xC4, 0xC8, 0x9E,
    0xEA, 0xBF, 0x8A, 0xD2, 0x40, 0xC7, 0x38, 0xB5, 0xA3, 0xF7, 0xF2, 0xCE, 0xF9, 0x61, 0x15, 0xA1,
    0xE0, 0xAE, 0x5D, 0xA4, 0x9B, 0x34, 0x1A, 0x55, 0xAD, 0x93, 0x32, 0x30, 0xF5, 0x8C, 0xB1, 0xE3,
    0x1D, 0xF6, 0xE2, 0x2E, 0x82, 0x66, 0xCA, 0x60, 0xC0, 0x29, 0x23, 0xAB, 0x0D, 0x53, 0x4E, 0x6F,
    0xD5, 0xDB, 0x37, 0x45, 0xDE, 0xFD, 0x8E, 0x2F, 0x03, 0xFF, 0x6A, 0x72, 0x6D, 0x6C, 0x5B, 0x51,
    0x8D, 0x1B, 0xAF, 0x92, 0xBB, 0xDD, 0xBC, 0x7F, 0x11, 0xD9, 0x5C, 0x41, 0x1F, 0x10, 0x5A, 0xD8,
    0x0A, 0xC1, 0x31, 0x88, 0xA5, 0xCD, 0x7B, 0xBD, 0x2D, 0x74, 0xD0, 0x12, 0xB8, 0xE5, 0xB4, 0xB0,
    0x89, 0x69, 0x97, 0x4A, 0x0C, 0x96, 0x77, 0x7E, 0x65, 0xB9, 0xF1, 0x09, 0xC5, 0x6E, 0xC6, 0x84,
    0x18, 0xF0, 0x7D, 0xEC, 0x3A, 0xDC, 0x4D, 0x20, 0x79, 0xEE, 0x5F, 0x3E, 0xD7, 0xCB, 0x39, 0x48,
]

_ROUND_KEYS = [
    0x818FA553, 0xEBA3318D, 0x5FC3C93A, 0xBD1DADD9,
    0xBB61CAB9, 0x000FD7EA, 0xDC6E0166, 0xDA937279,
    0x607EE786, 0xB548754C, 0x107330E4, 0xEA17C186,
    0x0F56F74B, 0xB21E443C, 0xE1210FE2, 0x009995C8,
    0xE7529A48, 0x6EF474F6, 0x2AB06DF6, 0x43B11BE8,
    0x359D4A14, 0xC29E2CDE, 0x30CF6A3E, 0x79D1C806,
    0x7C502387, 0xAAAB9BC6, 0xF0FE744B, 0x1CAFC872,
    0x95A9D075, 0x88070D58, 0x22800475, 0x8391938B,
]


def _rotl(v, bits):
    return ((v << bits) | (v >> (32 - bits))) & 0xFFFFFFFF


def _sm4_block(block):
    x = [int.from_bytes(block[i:i + 4], "big") for i in (0, 4, 8, 12)]
    for rk in _ROUND_KEYS:
        t = x[1] ^ x[2] ^ x[3] ^ rk
        b = ((_SBOX[(t >> 24) & 0xFF] << 24) | (_SBOX[(t >> 16) & 0xFF] << 16)
             | (_SBOX[(t >> 8) & 0xFF] << 8) | _SBOX[t & 0xFF])
        nx = x[0] ^ b ^ _rotl(b, 2) ^ _rotl(b, 10) ^ _rotl(b, 18) ^ _rotl(b, 24)
        x = [x[1], x[2], x[3], nx]
    return b"".join(v.to_bytes(4, "big") for v in (x[3], x[2], x[1], x[0]))


def derive_account_p12_password(account_id, uid):
    cn = hashlib.md5(account_id.encode("ascii")).hexdigest()
    app_input = cn + cn[0::2] + uid[1::2]
    digest = hashlib.sha256(app_input.encode("ascii")).digest()
    pad = 16 - (len(digest) % 16)
    padded = digest + bytes([pad]) * pad
    encoded = b"".join(_sm4_block(padded[i:i + 16]) for i in range(0, len(padded), 16))
    return base64.b64encode(encoded[:12]).decode("ascii")[:15]


# ---- Hash / KDF / firme ------------------------------------------------------------

def derive_sign_key(ikm, salt, info):
    """HKDF-SHA256 a 32 byte (una sola iterazione di expand)."""
    prk = hmac.new(salt.encode("utf-8"), ikm.encode("utf-8"), hashlib.sha256).digest()
    return hmac.new(prk, info.encode("utf-8") + b"\x01", hashlib.sha256).digest()


def hmac_hex(key, message):
    return hmac.new(key, message.encode("utf-8"), hashlib.sha256).hexdigest()


def sha256_hex(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def q(s):
    return quote(s, safe="")


def _nonce():
    return str(100000 + random.randrange(9899999))


def _headers(nonce, device_id, ts, sign):
    return {
        "acceptLanguage": LANGUAGE,
        "channel": CHANNEL,
        "deviceType": DEVICE_TYPE,
        "source": SOURCE,
        "version": APP_VERSION,
        "nonce": nonce,
        "deviceId": device_id,
        "timestamp": ts,
        "sign": sign,
        "X-P12_ENC_ALG": P12_ENC_ALG,
        "Content-Type": "application/x-www-form-urlencoded",
    }


def login_headers(device_id, username, password):
    n = _nonce()
    ts = str(int(time.time() * 1000))
    text = (LANGUAGE + DEVICE_TYPE + device_id + "1" + username + "0" + "1" + n
            + password + POLICY_ID + SOURCE + ts + APP_VERSION)
    return _headers(n, device_id, ts, sha256_hex(text))


def signed_headers(sign_key, device_id, vin=None):
    """Firma standard: valori dei campi ordinati per chiave, concatenati."""
    n = _nonce()
    ts = str(int(time.time() * 1000))
    fields = {
        "acceptLanguage": LANGUAGE,
        "channel": CHANNEL,
        "deviceId": device_id,
        "deviceType": DEVICE_TYPE,
        "nonce": n,
        "source": SOURCE,
        "timestamp": ts,
        "version": APP_VERSION,
    }
    if vin is not None:
        fields["vin"] = vin
    text = "".join(fields[k] for k in sorted(fields))
    return _headers(n, device_id, ts, hmac_hex(sign_key, text))


def session_device_id(token, fallback):
    """Il deviceId di sessione sta nel JWT, campo user_name, terzo elemento."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        parts = json.loads(base64.urlsafe_b64decode(payload)).get("user_name", "").split(",")
        if len(parts) >= 4 and parts[2]:
            return parts[2]
    except Exception:
        pass
    return fallback


# ---- Client --------------------------------------------------------------------------

class LeapCloud:
    """Una istanza per container Lambda: la sessione sopravvive fra le richieste."""

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.device_id = uuid.uuid4().hex
        self.http = requests.Session()
        self.app_cert = app_cert()
        self.account_cert = None
        self.user_id = None
        self.token = None
        self.sign_key = None
        self.vehicle = None  # (vin, carType)

    # -- HTTP --

    def _post(self, path, headers, body, cert, label):
        def send():
            return self.http.post(
                BASE_URL + path,
                headers=headers,
                data=body.encode("utf-8"),
                cert=cert,
                verify=False,  # server Leapmotor con certificati self-signed
                timeout=TIMEOUT,
            )
        try:
            try:
                resp = send()
            except requests.ConnectionError as exc:
                # Il gateway ogni tanto chiude la connessione appena aperta:
                # un secondo tentativo costa pochi decimi di secondo. Non sui
                # timeout, che raddoppiati sforerebbero gli 8 secondi di Alexa.
                if isinstance(exc, requests.Timeout):
                    raise
                resp = send()
        except requests.RequestException as exc:
            raise LeapError("rete", "%s: %s" % (label, exc))
        try:
            data = resp.json()
        except ValueError:
            raise LeapError("server", "%s: risposta non JSON (HTTP %s)" % (label, resp.status_code))
        if data.get("code", -1) != 0:
            msg = data.get("message") or resp.text[:160]
            raise LeapError("credenziali" if label == "login" else "server", "%s: %s" % (label, msg))
        return data

    def _auth(self, headers):
        headers["userId"] = self.user_id
        headers["token"] = self.token
        return headers

    # -- Sessione --

    def login(self):
        if self.app_cert is None:
            raise LeapError("certificati_app", "app.crt / app.key mancanti nella cartella lambda")
        body = ("isRecoverAcct=0"
                "&password=" + q(self.password)
                + "&policyId=" + POLICY_ID
                + "&loginMethod=1"
                + "&email=" + q(self.username))
        data = self._post(
            "/carownerservice/oversea/acct/v1/login",
            login_headers(self.device_id, self.username, self.password),
            body, self.app_cert, "login",
        ).get("data") or {}
        if not data.get("token"):
            raise LeapError("credenziali", "login senza token")

        self.user_id = str(data.get("id", ""))
        self.token = data["token"]
        self.device_id = session_device_id(self.token, self.device_id)
        self.sign_key = derive_sign_key(
            data.get("signIkm", ""), data.get("signSalt", ""), data.get("signInfo", ""))
        self._load_account_cert(data)

    def _load_account_cert(self, data):
        try:
            key, cert, _ = pkcs12.load_key_and_certificates(
                base64.b64decode(data.get("base64Cert", "")),
                derive_account_p12_password(str(data.get("id", "")), str(data.get("uid", ""))).encode("utf-8"),
            )
        except Exception as exc:
            raise LeapError("certificato", "p12: %s" % exc)
        if key is None or cert is None:
            raise LeapError("certificato", "p12 senza chiave o certificato")

        # requests vuole dei file: /tmp e' l'unica cartella scrivibile su Lambda.
        folder = tempfile.mkdtemp(prefix="leap_")
        cert_path = os.path.join(folder, "account_crt.pem")
        key_path = os.path.join(folder, "account_key.pem")
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        with open(key_path, "wb") as f:
            f.write(key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            ))
        self.account_cert = (cert_path, key_path)

    def _with_session(self, call):
        """Login se serve; se il cloud rifiuta il token, un secondo tentativo dopo il login."""
        if self.token is None:
            self.login()
            return call()
        try:
            return call()
        except LeapError as exc:
            if exc.kind in ("rete", "credenziali", "certificati_app"):
                raise
            self.login()
            return call()

    # -- Dati --

    def _vehicles(self):
        data = self._post(
            "/carownerservice/oversea/vehicle/v1/list",
            self._auth(signed_headers(self.sign_key, self.device_id)),
            "", self.account_cert, "elenco veicoli",
        ).get("data") or {}
        out = []
        for bucket in ("bindcars", "sharedcars"):
            for v in data.get(bucket) or []:
                if v.get("vin"):
                    out.append((v["vin"], v.get("carType", "")))
        return out

    def _pick_vehicle(self, wanted_vin):
        if self.vehicle is not None:
            return self.vehicle
        cars = self._vehicles()
        if not cars:
            raise LeapError("server", "nessun veicolo su questo account")
        if wanted_vin:
            cars = [c for c in cars if c[0].upper() == wanted_vin.upper()] or cars
        self.vehicle = cars[0]
        return self.vehicle

    def raw_status(self, wanted_vin=None):
        """Il campo `data` della risposta di stato, cosi' come arriva."""
        def call():
            vin, car_type = self._pick_vehicle(wanted_vin)
            t = car_type.upper()
            path = "c10" if t in ("B10", "B11", "B05") else (car_type.lower() or "c10")
            return self._post(
                "/carownerservice/oversea/vehicle/v1/status/get/" + path,
                self._auth(signed_headers(self.sign_key, self.device_id, vin=vin)),
                "vin=" + q(vin), self.account_cert, "stato veicolo",
            ).get("data") or {}
        return self._with_session(call)
