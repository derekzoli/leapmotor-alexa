# Leapmotor for Alexa

[Italiano](README.md) · **English** · [Español](README.es.md)

A **personal** Alexa skill to ask about your Leapmotor by voice and give it a few commands. It speaks **English, Italian and Spanish**.

| Say | Alexa answers |
|---|---|
| *"Alexa, ask my leapcar **how much charge it has**"* | "The battery is at 81 percent, with about 218 kilometres of range." If it's charging, it adds how long is left and up to what percentage. |
| *"Alexa, ask my leapcar **where the car is**"* | "The car is at Piazza Maggiore 1, Bologna", or "The car is at home" if you set up your places. The Alexa app also gets a card with a map link. |
| *"Alexa, ask my leapcar **if everything is OK**"* | Doors, windows, boot, tyres, whether it's locked (when parked) and whether the climate control is on. |
| *"Alexa, **open** my leapcar"* | All of the above at once. |
| *"Alexa, ask my leapcar to **lock the car**"* | Locks it, if it's parked and not already locked. |
| *"Alexa, ask my leapcar to **close the windows**"* | Closes them, if one is open. |
| *"Alexa, ask my leapcar to **turn on the heating to 22 degrees**"* | Also *the air conditioning*, or just *the climate control*: then it picks heating or cooling from the outside temperature. 18 to 32 degrees. |
| *"Alexa, ask my leapcar to **turn off the climate control**"* | Switches it off. |

Distances are in **kilometres** and temperatures in **degrees Celsius**.

If you gave your car a name in the official app, Alexa uses it in its answers: *"Elettra Lamborghini is locked."*

> 🔒 **No unlocking.** Commands only work if you switch them on, and even then the skill can only **lock** the car, **close** the windows and control the climate. Unlocking the car or opening the windows is deliberately not possible: anyone in the room can talk to a voice assistant, including the TV.

> ⚠️ **Unofficial project**, not affiliated with Leapmotor or Amazon. It uses undocumented Leapmotor cloud APIs that may change without notice. Tested on a **Leapmotor T03**; the code also reads the C10/B10 status format, but it hasn't been verified on those models.

Release notes (in Italian): [CHANGELOG.md](CHANGELOG.md).

---

## Installation

It takes about **half an hour**, once. You don't need to know how to program and it costs nothing: the skill runs for free on Amazon's servers, stays **private** to your account (no publishing, no certification) and works on all your Echo devices and in the Alexa app.

**In short, you will:**

1. create a second Leapmotor account, just for the skill;
2. download this project and the app certificates;
3. prepare the code zip;
4. create the skill in the Amazon developer console;
5. load the voice model (the phrases Alexa must understand) for each language you need;
6. upload the code and enter your details in `config.json`;
7. test it.

**Before you start you need:**

- [ ] the **Amazon** account your Echo devices use (email and password);
- [ ] a spare **email address**, for the new Leapmotor account;
- [ ] the official Leapmotor app on your phone;
- [ ] a **computer** (to download the files and use the Amazon console in the browser).

---

### Step 1 — A Leapmotor account just for the skill

**Why:** the Leapmotor cloud allows **only one session per account**. If the skill used your account, the skill and the official app on your phone would keep signing each other out.

1. In the official app, **sign out** and **create a new account** with the spare email.
2. Sign back in with **your** (owner) account and **share the car** with the new account.
3. Sign out and sign in with the **new** account: accept the terms and check that the car shows up.
4. **Only if you want commands** (locking, climate): still on the new account, set the **remote control PIN** in the app and try any command, to make sure the account is allowed to send them. Write the PIN down.
5. Sign out of the new account and back into yours. From now on the new account is used **only by the skill**: don't sign into it on your phone again, or the skill will be signed out.

✅ **Done when** you have the new account's email and password (and its PIN, if you want commands).

---

### Step 2 — Download the project and the certificates

1. At the top of this page: green button **Code → Download ZIP**. Extract it: you get a folder containing `lambda`, `skill-package` and the other files.
2. Open <https://github.com/markoceri/leapmotor-certs> and download the two files **`app.crt`** and **`app.key`**: click the file, then the *Download raw file* button (the down arrow on the right).
   They are the official app's certificates, needed to talk to the Leapmotor cloud; they aren't included here, out of respect for the people who extracted them.
3. Put `app.crt` and `app.key` in the project's **`lambda`** folder, next to `lambda_function.py`.

✅ **Done when** the `lambda` folder contains `app.crt`, `app.key`, `lambda_function.py`, `config.json` and the other `.py` files.

---

### Step 3 — Prepare the code zip

**Without installing anything (Windows):** right-click the **`lambda`** folder → *Compress to ZIP file* (or *Send to → Compressed (zipped) folder*). On a Mac: right-click → *Compress "lambda"*.

**With Python**, from the project folder:

```
python crea_zip.py
```

It creates `leapmotor-alexa-lambda.zip` and warns you if the certificates are missing.

⚠️ The zip must contain **the `lambda` folder**, not loose files. Compress the folder, not its contents: otherwise in step 6 the console says *"Your archive's root folder does not contain a lambda folder"*.

✅ **Done when** you have a `.zip` file that, when opened, shows the `lambda` folder.

---

### Step 4 — Create the skill in the Amazon console

1. Go to <https://developer.amazon.com/alexa/console/ask> and sign in **with the same Amazon account as your Echo devices**. The first time, it asks you to complete a developer profile: it's free.
2. Click **Create Skill** and follow the screens:
   - **Name, Locale**: any name (e.g. *MyLeapCar*); as language pick the one of your Echo, e.g. **English (UK)** or **English (US)** → *Next*.
   - **Experience, Model, Hosting service**:
     - *Choose a type of experience*: **Other**
     - *Choose a model*: **Custom**
     - *Hosting services*: **Alexa-hosted (Python)**
     - *Hosting region*: **EU (Ireland)** (the Leapmotor cloud is in Europe)

     → *Next*.
   - **Templates**: **Start from Scratch** → *Next* → **Create Skill**.
3. Wait a couple of minutes while Amazon sets up the skill.

✅ **Done when** you see the skill open, with the *Build*, *Code* and *Test* tabs at the top.

---

### Step 5 — Load the voice model

The voice model is the list of phrases Alexa must recognise. It lives in the `.json` files in `skill-package/interactionModels/custom/`, **one per language**:

| Language in the console | File to load |
|---|---|
| English (UK) | `en-GB.json` |
| English (US) | `en-US.json` |
| Italian (IT) | `it-IT.json` |
| Spanish (ES) | `es-ES.json` |

**5a. Only if you want more than one language:** open the language menu at the top left → **Language settings** → **Add new language** → add the ones you need → **Save**. Only add the languages of your Echo devices: an American Echo wants *English (US)*, a British one *English (UK)*.

**5b. For each language of the skill**, one at a time:

1. pick the language from the menu at the top left;
2. **Build** tab → on the left **Interaction Model** → **JSON Editor**;
3. drag in that language's file (see the table) and press **Save**.

**5c. Once every language has its file**, press **Build skill** and wait for *Build Successful*.

⚠️ **Build skill** builds **all** languages together: if one is still empty, it fails with *"Interaction Model does not include Custom Intents"*. Load all the files first, then build.

✅ **Done when** the build succeeds and, in every language, **Intents** on the left lists **BatteriaIntent**, **PosizioneIntent**, **AnomalieIntent**, **RiepilogoIntent**, **ChiudiAutoIntent**, **ChiudiFinestriniIntent**, **ClimaIntent**, **RiscaldamentoIntent**, **RaffreddamentoIntent**, **SpegniClimaIntent**. (The names are Italian: that's expected.)

The skill's name is already in the files: you don't have to set it by hand. You always say **"my leapcar"**; in the Italian and Spanish files, though, it's written **`my lipcar`**, because an Echo in Italian or Spanish transcribes "leapcar" that way (see *The skill's name*).

---

### Step 6 — Upload the code and enter your details

1. **Code** tab → **Import Code** → choose the zip from step 3 → leave all files selected → **Import**. If it asks to overwrite `lambda_function.py` and `requirements.txt`, confirm.
2. In the file list on the left open **`lambda/config.json`** and enter your details. The field names are in Italian; here's an example:

```json
{
  "email": "new-account-email@example.com",
  "password": "its-password",
  "vin": "",
  "nome": "",
  "comandi": true,
  "pin": "1234",
  "ventola": 3,
  "fuso_orario": 0,
  "luoghi": [
    { "nome": { "en": "at home", "it": "a casa", "es": "en casa" }, "lat": 51.523767, "lon": -0.158555, "raggio_m": 150 }
  ]
}
```

| Field | What to enter |
|---|---|
| `email`, `password` | those of the **new** Leapmotor account (step 1) |
| `comandi` (commands) | `true` to be able to lock the car, close the windows and control the climate; `false` for a skill that only answers questions |
| `pin` | the new account's remote control PIN, **in quotes**. Only needed with `"comandi": true` |
| `nome` (name) | optional. Empty = Alexa uses the name you gave the car in the official app (or "the car", if there isn't one). Only fill it in if you want a different name |
| `vin` | leave it empty, unless the account has more than one car |
| `ventola` (fan) | fan speed when Alexa switches on the climate control, 1 to 7 |
| `fuso_orario` (time zone) | `0` UK, Ireland and Portugal; `1` Italy, Spain and most of central Europe. Used to say the right time of the last contact with the car; daylight saving time is added automatically |
| `luoghi` (places) | optional. If the car is within `raggio_m` metres (radius) of a place, Alexa says its `nome` ("The car is at home") instead of the address. The name can be a single text (`"at home"`) or one per language, as in the example. You get the coordinates from `prova_locale.py` (below) or from Google Maps: right-click the spot → click the coordinates to copy them. If you don't need places, write `"luoghi": []` |

⚠️ Mind the commas and quotes: a mistake stops the skill from starting. Every line in a block except the last ends with a comma; texts go in double quotes. If the password contains `"`, write it as `\"`.

3. Press **Save**, then **Deploy**. Deploying takes about a minute (Amazon installs the libraries).

✅ **Done when** a successful deployment message appears at the top.

> Email, password and PIN stay in the private repository Amazon creates for your skill, visible only to your developer account.

---

### Step 7 — Test

1. **Test** tab → at the top, *Skill testing is enabled in*: switch from *Off* to **Development**.
2. In the box type, **without "Alexa"** in front:

   ```
   ask my leapcar how much charge it has
   ```

   It should answer with the battery level and the range.
3. Also try *open my leapcar*, *ask my leapcar if everything is OK* and, if you switched commands on, *ask my leapcar to lock the car*: if it's already locked it just tells you and sends nothing, so it's the safest test.
4. For other languages, pick the language from the menu next to *Development* and type e.g. `chiedi a my lipcar quanto è carica` or `pregunta a my lipcar dónde está el coche` (Italian and Spanish use the `my lipcar` spelling).
5. Now try it by voice on an Echo. You don't need to enable anything: skills in development are already active on your account (in the Alexa app: *More → Skills & Games → Your Skills → Dev*).

An Echo answers in **its own** language: to use the skill in another language, the Echo must be set to it (Alexa app → *Devices* → your Echo → *Language*).

> 💡 **Typing works but speaking doesn't?** It's a pronunciation problem, not a skill problem: the Echo transcribes the name differently from how it's written. **Change the invocation name** and write it exactly as your Echo transcribes it: you can see it in the voice history (Alexa app → *More → Settings → Alexa Privacy → Review Voice History*). Details in [The skill's name](#the-skills-name).

✅ **Done!** If something doesn't answer as expected, see [Troubleshooting](#troubleshooting).

---

### Optional — Test from your computer first

If you have Python, you can check the account, the shared car and the answers **before** steps 4–7:

```
pip install -r lambda/requirements.txt truststore
python prova_locale.py
```

It asks for the new account's email and password (it doesn't store them), signs in and reads the status the same way the skill will, and prints:

- what Alexa would say, in Italian, English and Spanish;
- the car's name and the commands the cloud allows it;
- the car's current coordinates, handy for `luoghi`.

It never sends commands to the car.

---

## Using the skill

### Phrases it understands

You don't need the exact words, but these are sure to work, after *"Alexa, ask my leapcar…"*:

| To | Phrases |
|---|---|
| Charge | how much charge it has · how much battery is left · what's the range · how many kilometres are left · is it charging · when will charging finish |
| Location | where the car is · where is my car · where did I park · where did I leave the car |
| Problems | if everything is OK · are there any problems · is the car locked · did I lock the car · is a window open · how are the tyres |
| Everything | how the car is · give me a summary · tell me everything |
| Locking | to lock the car · to lock the doors · to close the windows · to roll up the windows |
| Climate | to turn on the climate control to 21 degrees · to turn on the heating · to warm up the car to 23 degrees · to turn on the air conditioning at 20 degrees · to cool the car · to turn off the climate control |

The full list is in `en-GB.json`. After each answer the skill closes: for another question start again with *"Alexa, ask my leapcar…"*.

### What to expect from commands

- Alexa has about **8 seconds** to answer and the car sometimes takes longer to confirm. If the confirmation arrives in time you hear *"Done: the car is locked"*, otherwise *"I've sent the lock command to the car"*.
- The Leapmotor cloud replies "OK" even when the car ignores a command: **the real confirmation is asking for the status** a minute later (*"…if everything is OK"*).
- Before every command the skill reads the status: if the car is already locked or the climate control is already off, it tells you and sends nothing. If the car is moving, it won't lock it.
- If the PIN is rejected the skill **doesn't retry**: too many wrong PINs can block the account's remote commands.

---

## Updating to a new version

The [release notes](CHANGELOG.md) (in Italian) say what changed in each version and what to do. In general:

- **If the code changes** (almost always): **Code** tab → **first copy the contents of `config.json` somewhere safe** → **Import Code** with the new zip → put your details back into `config.json`, adding any new fields → **Save** → **Deploy**.
  ⚠️ Importing **overwrites** `config.json` with the placeholders: without the copy you'd have to re-enter email, password and PIN.
- **If the voice model changes** (new phrases or commands): for each language reload its `.json` in the JSON Editor and press **Save**, then **Build skill** once.

Adding languages (step 5a) is done only once.

---

## Customising

### The skill's name

"my leapcar" is the name you use to call the skill (*invocation name*). You change it in **Build → Invocations → Skill Invocation Name**, **in every language** (the console doesn't copy it from one to another), then **Build skill**. Rules learned the hard way:

- **write the name the way that language's Echo transcribes it.** Typing in the Alexa app always works, because the text matches; by voice it only works if the transcription matches the name. An Echo in Italian or Spanish hears "leapcar" as "lipcar", so `it-IT.json` and `es-ES.json` use `my lipcar`, while English keeps `my leapcar`. If your Echo transcribes it differently again, **change the invocation name** to match. To see how the Echo transcribes you: Alexa app → *More → Settings → Alexa Privacy → Review Voice History*;

- **at least two words**, all lowercase;
- **spelled the way they're pronounced**: a made-up word whose spelling doesn't match its sound isn't recognised;
- **no famous people's names**: the skill may lose to their music ("Alexa, open…");
- no "Alexa", "open", "ask", "skill".

If you change it, also update `invocationName` in the `.json` files, so reloading them doesn't bring back the old one.

### Adding phrases

If Alexa doesn't understand a phrase you use often, add it to the `samples` of the right intent in your language's file (or in *Build → Intents*), then **Save** and **Build skill**.

### Sharing with your family

Anyone using your Echo devices can already use the skill. For people with **another Amazon account** there's the console's **beta test** (*Distribution → Availability → Beta Test*): up to 500 people, no certification (but you must fill in the *Skill Preview* and *Privacy & Compliance* pages), invitation by link, at most **90 days** per beta (then you open another one).

Everyone will query **your** car. Anyone with their own Leapmotor must install their own copy by following this guide.

---

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Build: *"Interaction Model does not include Custom Intents"* | One of the skill's languages has no model: load its `.json` (step 5b), then **Build skill** again. |
| Import Code: *"Your archive's root folder does not contain a lambda folder"* | The zip contains loose files: compress the `lambda` **folder** (step 3). |
| Alexa: *"Sorry, I don't know that"* or similar | It doesn't recognise the skill's name: model not built (**Build skill**), testing not enabled (*Development*), or an unsuitable name (see *The skill's name*). |
| Typing it in the Alexa app works, **saying it doesn't** | The Echo transcribes the name differently. Check how it writes it in the voice history (Alexa app → *More → Settings → Alexa Privacy → Review Voice History*) and use exactly that spelling as the name for that language (see *The skill's name*). |
| Alexa answers every question with the help text | That language's model is missing the intents: reload its `.json` and build again. |
| *"There was a problem with the requested skill's response"* | The code doesn't start. Check the logs: Code tab → **CloudWatch Logs**, region *Europe (Ireland)*, latest log stream. |
| In the logs: `urllib3 v2 only supports OpenSSL 1.1.1+` | Old `requirements.txt`: it must contain `urllib3<2` (Alexa-hosted Python uses OpenSSL 1.0.2). |
| In the logs: `JSONDecodeError` | `config.json` isn't valid: check commas and quotes. |
| *"The skill isn't set up yet…"* | `config.json` still contains the placeholders (step 6). |
| *"The Leapmotor app certificates are missing…"* | `app.crt` and `app.key` weren't in the `lambda` folder when you made the zip (step 2). |
| *"I can't sign in to the Leapmotor account…"* | Wrong email or password, or the account was never opened in the official app (step 1). |
| *"Commands are switched off…"* / *"Commands need the vehicle PIN…"* | In `config.json` set `"comandi": true` and the PIN in quotes. |
| *"The Leapmotor cloud didn't accept the PIN"* | Wrong PIN, or the skill's account doesn't have one (step 1.4). Fix it **before** trying again. |
| *"Leapmotor doesn't allow this remote command for your car"* | The cloud doesn't grant that command to your car; `prova_locale.py` prints the allowed ones. |
| *"The Leapmotor cloud isn't responding right now…"* | The cloud is slow or unreachable: try again. |
| The official app on your phone signs you out | You're using the same account as the skill: use separate accounts (step 1). |
| Local test: `CERTIFICATE_VERIFY_FAILED` on the address | An antivirus that inspects HTTPS (e.g. Norton): install `truststore`. This doesn't happen on Amazon. |

---

## How it works

Alexa doesn't talk to your phone: for every question Amazon runs the skill's Python function, which signs in to the Leapmotor cloud with mutual TLS (app certificate, then account certificate), reads the car's status and answers in the Echo's language. The session stays open as long as Amazon keeps the function alive, so questions close together don't sign in again; a status read usually takes under a second. The address comes from OpenStreetMap (Nominatim), free and without a key.

The code is commented in Italian; the English phrases are all in `lambda/lingua_en.py`. The file map and the tests are described in the [Italian README](README.md#come-funziona).

## Credits

The Leapmotor cloud protocol was reverse-engineered by others, and the credit is theirs:

- [**markoceri/leapmotor-api**](https://github.com/markoceri/leapmotor-api): Python protocol library (signatures, HKDF, SM4), which `leapcloud.py` is derived from.
- [**markoceri/leapmotor-certs**](https://github.com/markoceri/leapmotor-certs): the app's TLS certificates.
- [**ProtossBlaster/leapmotor-mate**](https://github.com/ProtossBlaster/leapmotor-mate): field verification of the status signals.

## License

[GNU AGPL-3.0](LICENSE), the same as leapmotor-api, which the code is derived from.
