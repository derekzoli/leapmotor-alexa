# Leapmotor para Alexa

[Italiano](README.md) · [English](README.en.md) · **Español**

Skill de Alexa **personal** para preguntar por voz el estado de tu Leapmotor y darle algunas órdenes. Habla **español, italiano e inglés**.

| Dices | Alexa responde |
|---|---|
| *"Alexa, pregunta a my leapcar **cuánta batería tiene**"* | «La batería está al 81 por ciento, con unos 218 kilómetros de autonomía.» Si está cargando, añade cuánto falta y hasta qué porcentaje. |
| *"Alexa, pregunta a my leapcar **dónde está el coche**"* | «El coche está en Piazza Maggiore 1, Bolonia», o «El coche está en casa» si configuras tus lugares. En la app Alexa llega también una tarjeta con el enlace al mapa. |
| *"Alexa, pregunta a my leapcar **si está todo en orden**"* | Puertas, ventanillas, maletero, neumáticos, si está cerrado con llave (con el coche parado) y si el climatizador está encendido. |
| *"Alexa, **abre** my leapcar"* | Todo a la vez. |
| *"Alexa, pide a my leapcar **que cierre el coche**"* | Lo cierra con llave, si está parado y no está ya cerrado. |
| *"Alexa, pide a my leapcar **que cierre las ventanillas**"* | Las cierra, si hay alguna abierta. |
| *"Alexa, pide a my leapcar **que encienda la calefacción a 22 grados**"* | También *el aire acondicionado*, o solo *el climatizador*: entonces elige calor o frío según la temperatura exterior. De 18 a 32 grados. |
| *"Alexa, pide a my leapcar **que apague el climatizador**"* | Lo apaga. |

Si en la app oficial le has puesto un nombre al coche, Alexa lo usa en sus respuestas: *«Elettra Lamborghini tiene las puertas cerradas con llave.»*

> 🔒 **Nada de aperturas.** Los comandos solo funcionan si tú los activas, y aun así la skill solo puede **cerrar** el coche y las ventanillas y controlar el climatizador. Abrir el coche o las ventanillas no está previsto, a propósito: cualquiera que esté en la habitación puede hablar con un asistente de voz, también la tele.

> ⚠️ **Proyecto no oficial**, sin relación con Leapmotor ni con Amazon. Usa API no documentadas de la nube de Leapmotor, que pueden cambiar sin previo aviso. Probado en un **Leapmotor T03**; el código lee también el formato de estado de C10/B10, pero en esos modelos no se ha verificado.

Notas de las versiones (en italiano): [CHANGELOG.md](CHANGELOG.md).

---

## Instalación

Se tarda una **media hora**, una sola vez. No hace falta saber programar y no cuesta nada: la skill funciona gratis en los servidores de Amazon, queda **privada** en tu cuenta (sin publicarla ni certificarla) y funciona en todos tus Echo y en la app Alexa.

**En resumen, harás esto:**

1. crear una segunda cuenta de Leapmotor, solo para la skill;
2. descargar este proyecto y los certificados de la app;
3. preparar el zip del código;
4. crear la skill en la consola para desarrolladores de Amazon;
5. cargar el modelo de voz (las frases que Alexa tiene que entender) para cada idioma que necesites;
6. subir el código y escribir tus datos en `config.json`;
7. probarla.

**Antes de empezar necesitas:**

- [ ] la cuenta de **Amazon** de tus Echo (correo y contraseña);
- [ ] un **correo** adicional, para la nueva cuenta de Leapmotor;
- [ ] la app oficial de Leapmotor en el móvil;
- [ ] un **ordenador** (para descargar los archivos y usar la consola de Amazon en el navegador).

---

### Paso 1 — Una cuenta de Leapmotor solo para la skill

**Por qué:** la nube de Leapmotor mantiene **una sola sesión por cuenta**. Si la skill usara tu cuenta, la skill y la app oficial del móvil se desconectarían la una a la otra.

1. En la app oficial, **cierra sesión** y **crea una cuenta nueva** con el otro correo.
2. Vuelve a entrar con **tu** cuenta (la del propietario) y **comparte el coche** con la cuenta nueva.
3. Cierra sesión y entra con la cuenta **nueva**: acepta las condiciones y comprueba que aparece el coche.
4. **Solo si quieres los comandos** (cerrar, climatizador): con la cuenta nueva, configura en la app el **PIN de los comandos remotos** y prueba un comando cualquiera, para asegurarte de que esa cuenta puede enviarlos. Apunta el PIN.
5. Cierra la sesión de la cuenta nueva y vuelve a la tuya. A partir de ahora la cuenta nueva la usa **solo la skill**: no vuelvas a entrar con ella desde el móvil, o la skill se desconectará.

✅ **Listo cuando** tienes el correo y la contraseña de la cuenta nueva (y su PIN, si quieres los comandos).

---

### Paso 2 — Descarga el proyecto y los certificados

1. Arriba en esta página: botón verde **Code → Download ZIP**. Descomprímelo: obtienes una carpeta con `lambda`, `skill-package` y los demás archivos.
2. Abre <https://github.com/markoceri/leapmotor-certs> y descarga los dos archivos **`app.crt`** y **`app.key`**: haz clic en el archivo y luego en el botón *Download raw file* (la flecha hacia abajo, a la derecha).
   Son los certificados de la app oficial que hacen falta para hablar con la nube de Leapmotor; no se incluyen aquí, por respeto a quien los extrajo.
3. Pon `app.crt` y `app.key` en la carpeta **`lambda`** del proyecto, junto a `lambda_function.py`.

✅ **Listo cuando** la carpeta `lambda` contiene `app.crt`, `app.key`, `lambda_function.py`, `config.json` y los demás archivos `.py`.

---

### Paso 3 — Prepara el zip del código

**Sin instalar nada (Windows):** clic derecho sobre la carpeta **`lambda`** → *Comprimir en archivo ZIP* (o *Enviar a → Carpeta comprimida (en zip)*). En Mac: clic derecho → *Comprimir «lambda»*.

**Con Python**, desde la carpeta del proyecto:

```
python crea_zip.py
```

Crea `leapmotor-alexa-lambda.zip` y te avisa si faltan los certificados.

⚠️ El zip tiene que contener **la carpeta `lambda`**, no los archivos sueltos. Comprime la carpeta, no su contenido: si no, en el paso 6 la consola responde *"Your archive's root folder does not contain a lambda folder"*.

✅ **Listo cuando** tienes un archivo `.zip` que, al abrirlo, muestra la carpeta `lambda`.

---

### Paso 4 — Crea la skill en la consola de Amazon

La consola de Amazon está en inglés: aquí van los nombres tal como aparecen.

1. Ve a <https://developer.amazon.com/alexa/console/ask> y entra **con la misma cuenta de Amazon de tus Echo**. La primera vez te pide completar el perfil de desarrollador: es gratis.
2. Haz clic en **Create Skill** y sigue las pantallas:
   - **Name, Locale**: el nombre que quieras (por ejemplo *MyLeapCar*), idioma **Spanish (ES)** → *Next*.
   - **Experience, Model, Hosting service**:
     - *Choose a type of experience*: **Other**
     - *Choose a model*: **Custom**
     - *Hosting services*: **Alexa-hosted (Python)**
     - *Hosting region*: **EU (Ireland)** (la nube de Leapmotor está en Europa)

     → *Next*.
   - **Templates**: **Start from Scratch** → *Next* → **Create Skill**.
3. Espera un par de minutos mientras Amazon prepara la skill.

✅ **Listo cuando** ves la skill abierta, con las pestañas *Build*, *Code* y *Test* arriba.

---

### Paso 5 — Carga el modelo de voz

El modelo de voz es la lista de frases que Alexa tiene que reconocer. Está en los archivos `.json` de la carpeta `skill-package/interactionModels/custom/`, **uno por idioma**:

| Idioma en la consola | Archivo que cargar |
|---|---|
| Spanish (ES) | `es-ES.json` (sirve también para Spanish (MX) y (US)) |
| English (UK) | `en-GB.json` |
| English (US) | `en-US.json` |
| Italian (IT) | `it-IT.json` |

**5a. Solo si quieres más de un idioma:** abre el menú del idioma arriba a la izquierda → **Language settings** → **Add new language** → añade los que necesites → **Save**. Añade solo los idiomas de tus Echo.

**5b. Para cada idioma de la skill**, de uno en uno:

1. elige el idioma en el menú de arriba a la izquierda;
2. pestaña **Build** → a la izquierda **Interaction Model** → **JSON Editor**;
3. arrastra el archivo de ese idioma (mira la tabla) y pulsa **Save**.

**5c. Cuando todos los idiomas tengan su archivo**, pulsa **Build skill** y espera *Build Successful*.

⚠️ **Build skill** compila **todos** los idiomas a la vez: si uno sigue vacío, falla con *"Interaction Model does not include Custom Intents"*. Carga primero todos los archivos y luego compila.

✅ **Listo cuando** la compilación termina bien y, en cada idioma, en **Intents** a la izquierda aparecen **BatteriaIntent**, **PosizioneIntent**, **AnomalieIntent**, **RiepilogoIntent**, **ChiudiAutoIntent**, **ChiudiFinestriniIntent**, **ClimaIntent**, **RiscaldamentoIntent**, **RaffreddamentoIntent**, **SpegniClimaIntent**. (Los nombres están en italiano: es normal.)

El nombre de la skill ya está en los archivos: no hace falta configurarlo a mano. Siempre se dice **"my leapcar"**; en los archivos en español e italiano, sin embargo, está escrito **`my lipcar`**, porque un Echo en español o en italiano transcribe así "leapcar" (mira *El nombre de la skill*).

---

### Paso 6 — Sube el código y escribe tus datos

1. Pestaña **Code** → **Import Code** → elige el zip del paso 3 → deja seleccionados todos los archivos → **Import**. Si pregunta si quieres sobrescribir `lambda_function.py` y `requirements.txt`, confirma.
2. En la lista de archivos de la izquierda abre **`lambda/config.json`** y escribe tus datos. Los nombres de los campos están en italiano; aquí tienes un ejemplo:

```json
{
  "email": "correo-de-la-cuenta-nueva@ejemplo.es",
  "password": "su-contraseña",
  "vin": "",
  "nome": "",
  "comandi": true,
  "pin": "1234",
  "ventola": 3,
  "fuso_orario": 1,
  "luoghi": [
    { "nome": { "es": "en casa", "en": "at home", "it": "a casa" }, "lat": 40.416775, "lon": -3.703790, "raggio_m": 150 }
  ]
}
```

| Campo | Qué escribir |
|---|---|
| `email`, `password` | los de la cuenta **nueva** de Leapmotor (paso 1) |
| `comandi` (comandos) | `true` para poder cerrar el coche, las ventanillas y controlar el climatizador; `false` para una skill que solo responde a preguntas |
| `pin` | el PIN de los comandos remotos de la cuenta nueva, **entre comillas**. Solo hace falta con `"comandi": true` |
| `nome` (nombre) | opcional. Vacío = Alexa usa el nombre que le diste al coche en la app oficial (o «el coche», si no hay). Escríbelo solo si quieres otro nombre |
| `vin` | déjalo vacío, salvo que en la cuenta haya más de un coche |
| `ventola` (ventilador) | velocidad del ventilador cuando Alexa enciende el climatizador, de 1 a 7 |
| `fuso_orario` (huso horario) | `1` España peninsular, Italia y casi toda Europa central; `0` Canarias, Portugal, Reino Unido e Irlanda. Sirve para decir la hora correcta del último contacto con el coche; el horario de verano se suma solo |
| `luoghi` (lugares) | opcional. Si el coche está a menos de `raggio_m` metros (radio) de un lugar, Alexa dice su `nome` («El coche está en casa») en lugar de la dirección. El nombre puede ser uno solo (`"en casa"`) o uno por idioma, como en el ejemplo. Las coordenadas las sacas de `prova_locale.py` (más abajo) o de Google Maps: clic derecho en el punto → clic en las coordenadas para copiarlas. Si no necesitas lugares, escribe `"luoghi": []` |

⚠️ Cuidado con las comas y las comillas: un error impide que la skill arranque. Cada línea de un bloque, menos la última, termina con coma; los textos van entre comillas dobles. Si la contraseña contiene `"`, escríbela como `\"`.

3. Pulsa **Save** y luego **Deploy**. El despliegue tarda un minuto (Amazon instala las librerías).

✅ **Listo cuando** aparece arriba el mensaje de despliegue correcto.

> Correo, contraseña y PIN se quedan en el repositorio privado que Amazon crea para tu skill, visible solo para tu cuenta de desarrollador.

---

### Paso 7 — Prueba

1. Pestaña **Test** → arriba, *Skill testing is enabled in*: cambia de *Off* a **Development**.
2. En el recuadro escribe, **sin "Alexa"** delante:

   ```
   pregunta a my lipcar cuánta batería tiene
   ```

   Cuando **escribes**, en español usa `my lipcar`, es decir, el nombre tal como lo transcribe el Echo. Por voz dices "my leapcar".

   Tiene que responder con la batería y la autonomía.
3. Prueba también *abre my lipcar*, *pregunta a my lipcar si está todo en orden* y, si has activado los comandos, *pide a my lipcar que cierre el coche*: si ya está cerrado te lo dice y no envía nada, así que es la prueba más inofensiva.
4. Para otros idiomas, elige el idioma en el menú junto a *Development* y escribe por ejemplo `ask my leapcar how much charge it has` o `chiedi a my lipcar quanto è carica` (en italiano se escribe `my lipcar`).
5. Ahora pruébala por voz en un Echo. No tienes que activar nada: las skills en desarrollo ya están activas en tu cuenta (en la app Alexa: *Más → Skills y juegos → Tus skills → Desarrollo*).

Un Echo responde en **su** idioma: para usar la skill en otro idioma, el Echo tiene que estar configurado en él (app Alexa → *Dispositivos* → tu Echo → *Idioma*).

> 💡 **¿Escrito funciona pero por voz no?** Es un problema de interpretación de la pronunciación, no de la skill: el Echo transcribe el nombre de forma distinta a como está escrito. **Cambia el nombre de invocación** y escríbelo exactamente como lo transcribe tu Echo: lo ves en el historial de voz (app Alexa → *Más → Configuración → Privacidad de Alexa → Revisar el historial de voz*). Detalles en [El nombre de la skill](#el-nombre-de-la-skill).

✅ **¡Listo!** Si algo no responde como esperabas, mira [Si algo falla](#si-algo-falla).

---

### Opcional — Prueba antes desde el ordenador

Si tienes Python, puedes comprobar la cuenta, el coche compartido y las respuestas **antes** de los pasos 4–7:

```
pip install -r lambda/requirements.txt truststore
python prova_locale.py
```

Pide el correo y la contraseña de la cuenta nueva (no los guarda), entra y lee el estado como lo hará la skill, y muestra:

- lo que diría Alexa, en italiano, inglés y español;
- el nombre del coche y los comandos que la nube le permite;
- las coordenadas actuales del coche, útiles para `luoghi`.

Nunca envía comandos al coche.

---

## Usar la skill

### Frases que entiende

No hacen falta las palabras exactas, pero estas funcionan seguro, después de *"Alexa, pregunta a my leapcar…"* o *"Alexa, pide a my leapcar…"*:

| Para | Frases |
|---|---|
| Batería | cuánta batería tiene · cuánta autonomía le queda · cuántos kilómetros le quedan · si está cargando · cuándo termina la carga |
| Ubicación | dónde está el coche · dónde he aparcado · dónde he dejado el coche |
| Problemas | si está todo en orden · si hay algún problema · si está cerrado · si hay ventanillas abiertas · cómo están los neumáticos |
| Todo | cómo está el coche · hazme un resumen · dímelo todo |
| Cerrar | que cierre el coche · que bloquee las puertas · que cierre las ventanillas · que suba las ventanillas |
| Climatizador | que encienda el climatizador a 21 grados · que encienda la calefacción · que caliente el coche a 23 grados · que encienda el aire acondicionado a 20 grados · que enfríe el coche · que apague el climatizador |

La lista completa está en `es-ES.json`. Después de cada respuesta la skill se cierra: para otra pregunta vuelve a empezar con *"Alexa, pregunta a my leapcar…"*.

### Qué esperar de los comandos

- Alexa tiene unos **8 segundos** para responder y el coche a veces tarda más en confirmar. Si la confirmación llega a tiempo oyes *«Hecho: el coche tiene las puertas cerradas con llave»*, si no *«He enviado al coche la orden de cierre»*.
- La nube de Leapmotor responde "OK" incluso cuando el coche ignora un comando: **la confirmación de verdad es preguntar el estado** un minuto después (*"…si está todo en orden"*).
- Antes de cada comando la skill lee el estado: si el coche ya está cerrado o el climatizador ya está apagado, te lo dice y no envía nada. Si el coche está en movimiento, no lo cierra.
- Si el PIN es rechazado la skill **no lo vuelve a intentar**: demasiados PIN erróneos pueden bloquear los comandos remotos de la cuenta.

---

## Actualizar a una versión nueva

Las [notas de las versiones](CHANGELOG.md) (en italiano) dicen qué ha cambiado en cada versión y qué hacer. En general:

- **Si cambia el código** (casi siempre): pestaña **Code** → **primero copia en un sitio seguro el contenido de `config.json`** → **Import Code** con el zip nuevo → vuelve a poner tus datos en `config.json`, añadiendo los campos nuevos si los hay → **Save** → **Deploy**.
  ⚠️ Importar **sobrescribe** `config.json` con los valores de ejemplo: sin la copia tendrías que volver a escribir correo, contraseña y PIN.
- **Si cambia el modelo de voz** (frases o comandos nuevos): en cada idioma vuelve a cargar su `.json` en el JSON Editor y pulsa **Save**, y luego una vez **Build skill**.

Añadir idiomas (paso 5a) se hace una sola vez.

---

## Personalizar

### El nombre de la skill

"my leapcar" es el nombre con el que llamas a la skill (*invocation name*). Se cambia en **Build → Invocations → Skill Invocation Name**, **en cada idioma** (la consola no lo copia de uno a otro), y luego **Build skill**. Reglas aprendidas sobre la marcha:

- **el nombre se escribe como lo transcribe el Echo de ese idioma.** Escrito en la app Alexa siempre funciona, porque el texto coincide; por voz solo funciona si la transcripción coincide con el nombre. Un Echo en español o en italiano oye "leapcar" como "lipcar": por eso `es-ES.json` e `it-IT.json` usan `my lipcar`, mientras que en inglés sigue `my leapcar`. Si tu Echo lo transcribe de otra forma, **cambia el nombre de invocación** para que coincida. Para ver cómo lo transcribe: app Alexa → *Más → Configuración → Privacidad de Alexa → Revisar el historial de voz*;

- **al menos dos palabras**, todo en minúsculas;
- **escritas como se pronuncian**: una palabra inventada cuya ortografía no coincide con cómo suena no se reconoce;
- **nada de nombres de famosos**: la skill puede perder frente a su música («Alexa, abre…»);
- nada de "Alexa", "abre", "pregunta", "skill".

Si lo cambias, actualiza también `invocationName` en los archivos `.json`, para que al volver a cargarlos no vuelva el antiguo.

### Añadir frases

Si Alexa no entiende una frase que usas a menudo, añádela a los `samples` del intent correcto en el archivo de tu idioma (o en *Build → Intents*), y luego **Save** y **Build skill**.

### Compartir con la familia

Quien use tus Echo ya puede usar la skill. Para quien tenga **otra cuenta de Amazon** está la **beta** de la consola (*Distribution → Availability → Beta Test*): hasta 500 personas, sin certificación (pero hay que rellenar las páginas *Skill Preview* y *Privacy & Compliance*), invitación con un enlace, como máximo **90 días** por beta (luego se abre otra).

Todos consultarán **tu** coche. Quien tenga su propio Leapmotor tiene que instalar su propia copia siguiendo esta guía.

---

## Si algo falla

| Síntoma | Causa y solución |
|---|---|
| Build: *"Interaction Model does not include Custom Intents"* | Uno de los idiomas de la skill no tiene modelo: cárgale su `.json` (paso 5b) y vuelve a hacer **Build skill**. |
| Import Code: *"Your archive's root folder does not contain a lambda folder"* | El zip contiene archivos sueltos: comprime la **carpeta** `lambda` (paso 3). |
| Alexa: *«Lo siento, no lo sé»* o parecido | No reconoce el nombre de la skill: modelo sin compilar (**Build skill**), pruebas sin activar (*Development*) o un nombre poco adecuado (mira *El nombre de la skill*). |
| Escrito en la app Alexa funciona, **por voz no** | El Echo transcribe el nombre de otra forma. Mira cómo lo escribe en el historial de voz (app Alexa → *Más → Configuración → Privacidad de Alexa → Revisar el historial de voz*) y usa exactamente esa forma como nombre en ese idioma (mira *El nombre de la skill*). |
| Alexa responde con la ayuda a cualquier pregunta | Al modelo de ese idioma le faltan los intents: vuelve a cargar su `.json` y compila. |
| *«Ha habido un problema con la respuesta de la skill solicitada»* | El código no arranca. Mira los registros: pestaña Code → **CloudWatch Logs**, región *Europe (Ireland)*, el log stream más reciente. |
| En los registros: `urllib3 v2 only supports OpenSSL 1.1.1+` | `requirements.txt` antiguo: tiene que contener `urllib3<2` (el Python de Alexa-hosted usa OpenSSL 1.0.2). |
| En los registros: `JSONDecodeError` | `config.json` no es válido: revisa comas y comillas. |
| *«La skill todavía no está configurada…»* | `config.json` sigue con los valores de ejemplo (paso 6). |
| *«Faltan los certificados de la app de Leapmotor…»* | `app.crt` y `app.key` no estaban en la carpeta `lambda` cuando hiciste el zip (paso 2). |
| *«No consigo acceder a la cuenta de Leapmotor…»* | Correo o contraseña incorrectos, o la cuenta nunca se abrió en la app oficial (paso 1). |
| *«Los comandos están desactivados…»* / *«…hace falta el PIN…»* | En `config.json` pon `"comandi": true` y el PIN entre comillas. |
| *«La nube de Leapmotor no ha aceptado el PIN»* | PIN incorrecto, o la cuenta de la skill no tiene PIN (paso 1.4). Corrígelo **antes** de volver a intentarlo. |
| *«Leapmotor no permite este comando a distancia para tu coche»* | La nube no concede ese comando a tu coche; `prova_locale.py` muestra los permitidos. |
| *«La nube de Leapmotor no responde en este momento…»* | La nube va lenta o no está disponible: vuelve a intentarlo. |
| La app oficial del móvil te desconecta | Estás usando la misma cuenta que la skill: usa cuentas distintas (paso 1). |
| Prueba local: `CERTIFICATE_VERIFY_FAILED` en la dirección | Un antivirus que inspecciona el HTTPS (por ejemplo Norton): instala `truststore`. En Amazon no pasa. |

---

## Cómo funciona

Alexa no habla con tu móvil: en cada pregunta Amazon ejecuta la función Python de la skill, que entra en la nube de Leapmotor con TLS mutuo (certificado de la app y luego de la cuenta), lee el estado del coche y responde en el idioma del Echo. La sesión sigue abierta mientras Amazon mantiene viva la función, así que las preguntas seguidas no vuelven a iniciar sesión; una lectura suele tardar menos de un segundo. La dirección viene de OpenStreetMap (Nominatim), gratis y sin clave.

El código está comentado en italiano; las frases en español están todas en `lambda/lingua_es.py`. Como «el coche» es masculino, las frases hablan de lo que el coche *tiene* («tiene las puertas cerradas con llave»), para que suenen bien también con nombres femeninos. El mapa de los archivos y las pruebas están descritos en el [README en italiano](README.md#come-funziona).

## Créditos

El protocolo de la nube de Leapmotor lo reconstruyeron otros, y el mérito es suyo:

- [**markoceri/leapmotor-api**](https://github.com/markoceri/leapmotor-api): librería Python del protocolo (firmas, HKDF, SM4), de la que deriva `leapcloud.py`.
- [**markoceri/leapmotor-certs**](https://github.com/markoceri/leapmotor-certs): certificados TLS de la app.
- [**ProtossBlaster/leapmotor-mate**](https://github.com/ProtossBlaster/leapmotor-mate): verificación sobre el terreno de las señales de estado.

## Licencia

[GNU AGPL-3.0](LICENSE), la misma que leapmotor-api, de la que deriva el código.
