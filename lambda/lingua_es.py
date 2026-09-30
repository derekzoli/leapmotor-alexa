"""Frases en español (de España). Mismas funciones que lingua_it.py.

"El coche" es masculino: para no concordar adjetivos con el nombre del coche
(que puede sonar femenino, como "Elettra Lamborghini"), las frases hablan de
lo que el coche TIENE ("tiene las puertas cerradas con llave").
"""

from comune import cap, cose_aperte, durata, elenco, non_chiusa

CODICE = "es"
MAPPA = "Mapa"
CIAO = "¡Hasta luego!"

AIUTO = ("Puedes preguntarme cuánta batería tiene el coche, dónde está "
         "o si todo está en orden. También puedo cerrarlo, cerrar las ventanillas "
         "y encender o apagar el climatizador. ¿Qué quieres hacer?")
NON_CONFIGURATA = ("La skill todavía no está configurada: escribe el correo y la contraseña "
                   "de la cuenta de Leapmotor en el archivo config punto json.")
COMANDI_OFF = "Los comandos están desactivados en la configuración de la skill."
SERVE_PIN = "Para los comandos hace falta el PIN del vehículo en el archivo de configuración."
IMPREVISTO = "Algo ha fallado al consultar el coche. Vuelve a intentarlo en un rato."

ERRORI = {
    "rete": "La nube de Leapmotor no responde en este momento. Vuelve a intentarlo en un rato.",
    "credenziali": ("No consigo acceder a la cuenta de Leapmotor. "
                    "Revisa el correo y la contraseña en el archivo de configuración de la skill."),
    "certificati_app": ("Faltan los certificados de la app de Leapmotor en la carpeta lambda. "
                        "Encontrarás las instrucciones en la página del proyecto."),
    "certificato": "La nube de Leapmotor ha enviado un certificado que no puedo abrir.",
    "pin": ("La nube de Leapmotor no ha aceptado el PIN. Revísalo en el archivo de configuración "
            "antes de volver a intentarlo: demasiados intentos fallidos pueden bloquear los "
            "comandos remotos."),
    "non_consentito": "Leapmotor no permite este comando a distancia para tu coche.",
    "sessione": "La sesión con la nube de Leapmotor ha caducado. Vuelve a intentarlo.",
    "server": "La nube de Leapmotor ha respondido con un error. Vuelve a intentarlo en un rato.",
}

RUOTE = {"ant_sx": "delantero izquierdo", "ant_dx": "delantero derecho",
         "post_sx": "trasero izquierdo", "post_dx": "trasero derecho"}
MESI = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
        "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

CONFERMA_STATO = " Dentro de un minuto pregúntame si todo está en orden para confirmarlo."


def soggetto(nome):
    return nome or "el coche"


def a_soggetto(nome):
    return ("a " + nome) if nome else "al coche"


def di_soggetto(nome):
    return ("de " + nome) if nome else "del coche"


def _durata(minuti):
    return durata(minuti, "una hora", "%d horas", "un minuto", "%d minutos", "y")


# ---- Estado -------------------------------------------------------------------

def batteria(s, nome=None):
    if s.soc is None:
        return "No recibo el nivel de batería del coche."
    if nome:
        frase = "%s tiene la batería al %d por ciento" % (nome, s.soc)
    else:
        frase = "La batería está al %d por ciento" % s.soc
    if s.autonomia_km:
        frase += ", con unos %d kilómetros de autonomía" % s.autonomia_km
    frase += "."
    if s.in_carica:
        frase += " Está cargando"
        if s.minuti_a_fine_carica:
            frase += " y terminará en unos %s" % _durata(s.minuti_a_fine_carica)
            if s.limite_carica:
                frase += ", al %d por ciento" % s.limite_carica
        frase += "."
    elif s.cavo_collegato:
        frase += " El cable está conectado pero no está cargando"
        if s.limite_carica and s.soc >= s.limite_carica:
            frase += ": ha llegado al límite configurado"
        frase += "."
    return frase


def indirizzo(a):
    """ "en Piazza Maggiore 1, Bolonia"."""
    via = a.get("road") or a.get("pedestrian") or a.get("square")
    civico = a.get("house_number")
    paese = (a.get("city") or a.get("town") or a.get("village")
             or a.get("municipality") or a.get("hamlet"))
    if via and civico:
        via = "%s %s" % (via, civico)
    parti = [p for p in (via, paese) if p]
    return ("en " + ", ".join(parti)) if parti else None


def posizione(s, luogo, dove, nome=None):
    chi = cap(soggetto(nome))
    if s.lat is None or s.lon is None:
        return "%s no comunica su ubicación en este momento." % chi
    movimento = " y se está moviendo" if s.in_movimento else ""
    if luogo:
        return "%s está %s%s." % (chi, luogo, movimento)
    if dove:
        return "%s está %s%s." % (chi, dove, movimento)
    frase = ("No consigo obtener la dirección %s, pero tienes la ubicación en la tarjeta "
             "de la app Alexa." % di_soggetto(nome))
    if s.in_movimento:
        frase += " %s se está moviendo." % chi
    return frase


def _voci(s):
    voci = []
    for v in cose_aperte(s):
        if v == "portiera":
            voci.append("una puerta abierta")
        elif v == "finestrino":
            voci.append("una ventanilla abierta")
        elif v == "baule":
            voci.append("el maletero abierto")
        else:
            ruote = [RUOTE[r] for r in s.gomme_anomale]
            if len(ruote) == 1:
                voci.append("una presión anómala en el neumático %s" % ruote[0])
            else:
                voci.append("una presión anómala en los neumáticos %s" % elenco(ruote, "y"))
    return voci


def clima(s):
    if not s.clima_acceso:
        return ""
    if s.temp_clima:
        return "El climatizador está encendido a %d grados." % s.temp_clima
    return "El climatizador está encendido."


def anomalie(s, nome=None, sottinteso=False):
    """sottinteso=True: sin repetir el sujeto, para el resumen."""
    chi = "" if sottinteso else soggetto(nome) + " "
    voci = _voci(s)
    if voci:
        frase = "Atención: %stiene %s" % (chi, elenco(voci, "y"))
        if non_chiusa(s):
            frase += ", y las puertas no están cerradas con llave"
        frase += "."
    elif non_chiusa(s):
        if sottinteso:
            frase = "Atención: las puertas no están cerradas con llave."
        else:
            frase = "Atención: las puertas %s no están cerradas con llave." % di_soggetto(nome)
    elif s.in_movimento:
        frase = "Ninguna anomalía: %sestá en movimiento, con puertas y ventanillas cerradas." % chi
    elif s.chiusa:
        if sottinteso:
            frase = "Todo en orden: puertas cerradas con llave, ventanillas y maletero cerrados."
        else:
            frase = ("Todo en orden: %stiene las puertas cerradas con llave, "
                     "y las ventanillas y el maletero cerrados." % chi)
    else:
        frase = "Todo en orden: puertas, ventanillas y maletero están cerrados."
    c = clima(s)
    return frase + (" " + c if c else "")


def eta(quando, oggi, ieri):
    orario = "%d:%02d" % (quando.hour, quando.minute)
    if quando.date() == oggi:
        giorno = "hoy"
    elif quando.date() == ieri:
        giorno = "ayer"
    else:
        giorno = "el %d de %s" % (quando.day, MESI[quando.month - 1])
    return "El último contacto con el coche fue %s a las %s." % (giorno, orario)


# ---- Comandos -----------------------------------------------------------------

def in_movimento(nome):
    return "%s está en movimiento: no lo cierro a distancia." % cap(soggetto(nome))


def gia_chiusa(nome):
    return "%s ya tiene las puertas cerradas con llave." % cap(soggetto(nome))


AVVISO_PORTIERA = "Atención, parece que hay una puerta abierta: puede que el cierre no funcione. "


def chiusa_fatto(nome):
    return "Hecho: %s tiene las puertas cerradas con llave." % soggetto(nome)


def chiusa_inviato(nome):
    return "He enviado %s la orden de cierre." % a_soggetto(nome) + CONFERMA_STATO


FINESTRINI_GIA = "Las ventanillas ya están cerradas."
FINESTRINI_FATTO = "Hecho: ventanillas cerradas."


def finestrini_inviato(nome):
    return "He enviado %s la orden de cerrar las ventanillas." % a_soggetto(nome) + CONFERMA_STATO


SPENTO_GIA = "El climatizador ya está apagado."
SPENTO_FATTO = "Hecho: climatizador apagado."


def spento_inviato(nome):
    return "He enviado %s la orden de apagar el climatizador." % a_soggetto(nome) + CONFERMA_STATO


_IMPIANTI = {"clima": ("climatizador", "encendido"), "caldo": ("calefacción", "encendida"),
             "freddo": ("aire acondicionado", "encendido")}


def acceso_fatto(impianto, gradi):
    nome, acceso = _IMPIANTI[impianto]
    return "Hecho: %s %s a %d grados." % (nome, acceso, gradi)


def acceso_inviato(nome, impianto, gradi):
    return "He enviado %s: %s a %d grados." % (a_soggetto(nome), _IMPIANTI[impianto][0], gradi) + CONFERMA_STATO


TEMP_NON_CAPITA = "No he entendido la temperatura."


def temp_fuori(minimo, massimo):
    return "Puedo poner el climatizador entre %d y %d grados." % (minimo, massimo)
