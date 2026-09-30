"""Indirizzo dalle coordinate, con OpenStreetMap (Nominatim): gratis, senza chiave."""

import requests

_cache = {}


def indirizzo(lat, lon, lingua="it"):
    """Il blocco `address` di Nominatim, nella lingua data ("Bologna" / "Bolonia"),
    o None se il servizio non risponde in fretta."""
    # ~10 m: l'auto parcheggiata non rifa' la richiesta
    chiave = (round(lat, 4), round(lon, 4), lingua)
    if chiave in _cache:
        return _cache[chiave]
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "jsonv2", "zoom": 18,
                    "addressdetails": 1, "accept-language": lingua},
            # La policy di Nominatim chiede un User-Agent che identifichi l'applicazione.
            headers={"User-Agent": "MyLeapCar-Alexa/1.0 (skill personale)"},
            timeout=(2, 2),
        )
        address = resp.json().get("address") if resp.ok else None
    except (requests.RequestException, ValueError):
        return None
    if address:
        _cache[chiave] = address
    return address


def link_mappa(lat, lon):
    return "https://maps.google.com/?q=%.6f,%.6f" % (lat, lon)
