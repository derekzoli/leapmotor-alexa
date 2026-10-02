# Leapmotor per Alexa

**Italiano** · [English](README.en.md) · [Español](README.es.md)

Skill Alexa **personale** per chiedere a voce lo stato della tua Leapmotor e darle qualche comando. Parla **italiano, inglese e spagnolo**.

| Chiedi | Alexa risponde |
|---|---|
| *"Alexa, chiedi a my leapcar **quanto è carica**"* | «La batteria è all'81 per cento, circa 218 chilometri di autonomia.» Se è in carica aggiunge quanto manca e fino a che percentuale. |
| *"Alexa, chiedi a my leapcar **dov'è la macchina**"* | «L'auto si trova in Piazza Maggiore 1, a Bologna», oppure «L'auto è a casa» se configuri i tuoi luoghi. Nell'app Alexa arriva anche il link alla mappa. |
| *"Alexa, chiedi a my leapcar **se è tutto a posto**"* | Portiere, finestrini, baule, gomme, chiusura a chiave (a veicolo fermo) e clima acceso. |
| *"Alexa, **apri** my leapcar"* | Tutto insieme. |
| *"Alexa, chiedi a my leapcar di **chiudere l'auto**"* | La chiude a chiave, se è ferma e non è già chiusa. |
| *"Alexa, chiedi a my leapcar di **chiudere i finestrini**"* | Li chiude, se ce n'è uno aperto. |
| *"Alexa, chiedi a my leapcar di **accendere il riscaldamento a 22 gradi**"* | Anche *l'aria condizionata*, o solo *il clima*: allora sceglie caldo o freddo in base alla temperatura esterna. Da 18 a 32 gradi. |
| *"Alexa, chiedi a my leapcar di **spegnere il clima**"* | Lo spegne. |

**English** (kilometres, °C): *"Alexa, ask my leapcar how much charge it has"* · *"…where is the car"* · *"…if everything is OK"* · *"…to lock the car"* · *"…to turn on the heating to 21 degrees"*

**Español**: *"Alexa, pregunta a my leapcar cuánta batería tiene"* · *"…dónde está el coche"* · *"…si está todo en orden"* · *"Alexa, pide a my leapcar que cierre el coche"* · *"…que encienda la calefacción a 21 grados"*

Se nell'app ufficiale hai dato un nome all'auto, Alexa lo usa anche nelle risposte: *«Elettra Lamborghini è chiusa a chiave.»*

> 🔒 **Niente aperture.** I comandi si accendono solo se lo decidi tu, e anche così la skill può soltanto **chiudere** l'auto e i finestrini e comandare il clima. Aprire l'auto o i finestrini non è previsto, di proposito: una skill vocale la può usare chiunque sia nella stanza, compresa la TV.

> ⚠️ **Progetto non ufficiale**, senza alcun rapporto con Leapmotor o Amazon. Usa API del cloud Leapmotor non documentate, che possono cambiare senza preavviso. Provato su una **Leapmotor T03**; il codice legge anche il formato di stato di C10/B10, ma su quei modelli non è stato verificato.

Cosa è cambiato tra una versione e l'altra: [note degli aggiornamenti](CHANGELOG.md).

---

## Installazione

Ci vuole circa **mezz'ora**, una volta sola. Non serve saper programmare e non si paga niente: la skill gira gratis sui server di Amazon, resta **privata** sul tuo account (niente pubblicazione, niente certificazione) e funziona su tutti i tuoi Echo e nell'app Alexa.

**In breve, farai questo:**

1. crei un secondo account Leapmotor, solo per la skill;
2. scarichi questo progetto e i certificati dell'app;
3. prepari lo zip del codice;
4. crei la skill nella console per sviluppatori Amazon;
5. carichi il modello vocale (le frasi che Alexa deve capire), per ogni lingua che ti serve;
6. carichi il codice e scrivi i tuoi dati in `config.json`;
7. provi.

**Prima di iniziare ti servono:**

- [ ] l'account **Amazon** dei tuoi Echo (email e password);
- [ ] un'**email** in più, per il nuovo account Leapmotor;
- [ ] l'app ufficiale Leapmotor sul telefono;
- [ ] un **PC** (per scaricare i file e usare la console Amazon dal browser).

---

### Passo 1 — Un account Leapmotor solo per la skill

**Perché:** il cloud Leapmotor tiene **una sola sessione per account**. Se la skill usasse il tuo account, lei e l'app ufficiale sul telefono si butterebbero fuori a vicenda.

1. Nell'app ufficiale, **esci** e **crea un nuovo account** con l'altra email.
2. Rientra con il **tuo** account (quello proprietario) e **condividi l'auto** con il nuovo account.
3. Esci ed entra con il **nuovo** account: accetta i termini e controlla che l'auto compaia.
4. **Solo se vuoi i comandi** (chiudere, clima): sempre con il nuovo account, imposta nell'app il **PIN dei comandi remoti** e prova un comando qualsiasi, per esser sicuro che l'account li possa dare. Annotati il PIN.
5. Esci dal nuovo account e rientra con il tuo. D'ora in poi il nuovo account lo usa **solo la skill**: non entrarci più dal telefono, o la skill verrà scollegata.

✅ **Fatto quando** hai: email e password del nuovo account (e il suo PIN, se vuoi i comandi).

---

### Passo 2 — Scarica il progetto e i certificati

1. In cima a questa pagina: pulsante verde **Code → Download ZIP**. Estrai l'archivio: ottieni una cartella con dentro `lambda`, `skill-package` e gli altri file.
2. Apri <https://github.com/markoceri/leapmotor-certs> e scarica i due file **`app.crt`** e **`app.key`**: clicca sul file, poi sul pulsante *Download raw file* (la freccia verso il basso, a destra).
   Sono i certificati dell'app ufficiale che servono per parlare con il cloud Leapmotor; non sono inclusi qui, per rispetto di chi li ha estratti.
3. Metti `app.crt` e `app.key` nella cartella **`lambda`** del progetto, accanto a `lambda_function.py`.

✅ **Fatto quando** la cartella `lambda` contiene `app.crt`, `app.key`, `lambda_function.py`, `config.json` e gli altri file `.py`.

---

### Passo 3 — Prepara lo zip del codice

**Senza installare niente (Windows):** tasto destro sulla cartella **`lambda`** → *Comprimi in file ZIP* (o *Invia a → Cartella compressa*).

**Con Python**, dalla cartella del progetto:

```
python crea_zip.py
```

Crea `leapmotor-alexa-lambda.zip` e ti avvisa se mancano i certificati.

⚠️ Lo zip deve contenere **la cartella `lambda`**, non i file sciolti. Comprimi la cartella, non il suo contenuto: altrimenti al passo 6 la console risponde *"Your archive's root folder does not contain a lambda folder"*.

✅ **Fatto quando** hai un file `.zip` che, aperto, mostra la cartella `lambda`.

---

### Passo 4 — Crea la skill nella console Amazon

1. Vai su <https://developer.amazon.com/alexa/console/ask> e accedi **con lo stesso account Amazon dei tuoi Echo**. La prima volta ti chiede di completare il profilo sviluppatore: è gratuito.
2. Clicca **Create Skill** e segui le schermate:
   - **Name, Locale**: nome a piacere (per esempio *MyLeapCar*), lingua **Italian (IT)** → *Next*.
   - **Experience, Model, Hosting service**:
     - *Choose a type of experience*: **Other**
     - *Choose a model*: **Custom**
     - *Hosting services*: **Alexa-hosted (Python)**
     - *Hosting region*: **EU (Ireland)**

     → *Next*.
   - **Templates**: **Start from Scratch** → *Next* → **Create Skill**.
3. Aspetta un paio di minuti mentre Amazon prepara la skill.

✅ **Fatto quando** vedi la skill aperta, con le schede *Build*, *Code*, *Test* in alto.

---

### Passo 5 — Carica il modello vocale

Il modello vocale è l'elenco delle frasi che Alexa deve riconoscere. È nei file `.json` della cartella `skill-package/interactionModels/custom/`, **uno per lingua**:

| Lingua nella console | File da caricare |
|---|---|
| Italian (IT) | `it-IT.json` |
| English (UK) | `en-GB.json` |
| English (US) | `en-US.json` |
| Spanish (ES) | `es-ES.json` |

**5a. Solo se vuoi altre lingue oltre all'italiano:** in alto a sinistra apri il menu della lingua (*Italian (IT)*) → **Language settings** → **Add new language** → aggiungi quelle che ti servono → **Save**. Aggiungi solo le lingue dei tuoi Echo: un Echo in inglese americano vuole *English (US)*, uno britannico *English (UK)*.

**5b. Per ogni lingua della skill**, una alla volta:

1. scegli la lingua dal menu in alto a sinistra;
2. scheda **Build** → a sinistra **Interaction Model** → **JSON Editor**;
3. trascina dentro il file di quella lingua (vedi tabella) e premi **Save**.

**5c. Quando tutte le lingue hanno il loro file**, premi **Build skill** e aspetta *Build Successful*.

⚠️ **Build skill** compila **tutte** le lingue insieme: se una è ancora vuota, fallisce con *"Interaction Model does not include Custom Intents"*. Carica prima tutti i file, poi fai la build.

✅ **Fatto quando** la build riesce e, in ogni lingua, sotto *Intents* a sinistra compaiono **BatteriaIntent**, **PosizioneIntent**, **AnomalieIntent**, **RiepilogoIntent**, **ChiudiAutoIntent**, **ChiudiFinestriniIntent**, **ClimaIntent**, **RiscaldamentoIntent**, **RaffreddamentoIntent**, **SpegniClimaIntent**.

Il nome della skill è già scritto nei file: non devi impostarlo a mano. A voce si dice sempre **"my leapcar"**; nei file italiano e spagnolo però è scritto **`my lipcar`**, perché un Echo in italiano o in spagnolo trascrive così "leapcar" (vedi *Il nome della skill*).

---

### Passo 6 — Carica il codice e scrivi i tuoi dati

1. Scheda **Code** → **Import Code** → scegli lo zip del passo 3 → lascia selezionati tutti i file → **Import**. Se chiede di sovrascrivere `lambda_function.py` e `requirements.txt`, conferma.
2. Nell'elenco dei file a sinistra apri **`lambda/config.json`** e scrivi i tuoi dati. Per esempio:

```json
{
  "email": "email-del-nuovo-account@esempio.it",
  "password": "la-sua-password",
  "vin": "",
  "nome": "",
  "comandi": true,
  "pin": "1234",
  "ventola": 3,
  "fuso_orario": 1,
  "luoghi": [
    { "nome": { "it": "a casa", "en": "at home", "es": "en casa" }, "lat": 44.493889, "lon": 11.342778, "raggio_m": 150 }
  ]
}
```

| Campo | Cosa scrivere |
|---|---|
| `email`, `password` | quelle del **nuovo** account Leapmotor (passo 1) |
| `comandi` | `true` per poter chiudere l'auto, i finestrini e comandare il clima; `false` per una skill che risponde solo alle domande |
| `pin` | il PIN dei comandi remoti del nuovo account, **tra virgolette**. Serve solo con `"comandi": true` |
| `nome` | facoltativo. Vuoto = Alexa usa il nome dato all'auto nell'app ufficiale (o «l'auto», se non c'è). Scrivi un nome solo se ne vuoi uno diverso |
| `vin` | lascialo vuoto, a meno che sull'account ci siano più auto |
| `ventola` | velocità della ventola quando Alexa accende il clima, da 1 a 7 |
| `fuso_orario` | `1` Italia e Spagna, `0` Regno Unito, Irlanda e Portogallo. Serve a dire l'ora giusta dell'ultimo contatto con l'auto; l'ora legale si aggiunge da sola |
| `luoghi` | facoltativo. Se l'auto è entro `raggio_m` metri da un luogo, Alexa dice il suo `nome` («L'auto è a casa») invece dell'indirizzo. Il nome può essere unico (`"a casa"`) o uno per lingua, come nell'esempio. Le coordinate di casa le trovi con `prova_locale.py` (più sotto) o da Google Maps: tasto destro sul punto → clicca le coordinate per copiarle. Se non ti servono, lascia `"luoghi": []` |

⚠️ Attenzione a virgole e virgolette: un errore blocca la skill all'avvio. Ogni riga tranne l'ultima di un blocco finisce con la virgola; i testi vanno tra virgolette doppie. Se la password contiene `"`, scrivila come `\"`.

3. Premi **Save**, poi **Deploy**. Il deploy dura circa un minuto (Amazon installa le librerie).

✅ **Fatto quando** in alto compare il messaggio di deploy riuscito.

> Email, password e PIN restano nel repository privato che Amazon crea per la tua skill, visibile solo al tuo account sviluppatore.

---

### Passo 7 — Prova

1. Scheda **Test** → in alto, *Skill testing is enabled in*: passa da *Off* a **Development**.
2. Nel riquadro scrivi, **senza "Alexa"** davanti:

   ```
   chiedi a my lipcar quanto è carica
   ```

   Quando **scrivi**, in italiano usa `my lipcar`, cioè il nome come lo trascrive l'Echo. A voce dici "my leapcar".

   Deve rispondere con la batteria e l'autonomia.
3. Prova anche *apri my lipcar*, *chiedi a my lipcar se è tutto a posto* e, se hai attivato i comandi, *chiedi a my lipcar di chiudere l'auto*: se è già chiusa te lo dice e non manda niente, quindi è la prova più innocua.
4. Per le altre lingue, scegli la lingua dal menu accanto a *Development* e scrivi per esempio `ask my leapcar how much charge it has` o `pregunta a my lipcar dónde está el coche` (anche in spagnolo, scritto, è `my lipcar`).
5. Ora prova a voce su un Echo. Non devi attivare niente: le skill in sviluppo sono già attive sul tuo account (nell'app Alexa la trovi in *Altro → Skill e giochi → Le tue skill → Sviluppatore*).

Un Echo risponde nella **sua** lingua: per usare la skill in inglese o spagnolo l'Echo dev'essere impostato in quella lingua (app Alexa → *Dispositivi* → il tuo Echo → *Lingua*).

> 💡 **Scritto funziona ma a voce no?** È un problema di interpretazione della pronuncia, non della skill: l'Echo trascrive il nome in modo diverso da come è scritto. **Cambia l'invocazione** e scrivila esattamente come la trascrive il tuo Echo: lo vedi nella cronologia vocale (app Alexa → *Altro → Impostazioni → Privacy Alexa → Rivedi la cronologia vocale*). Dettagli in [Il nome della skill](#il-nome-della-skill).

✅ **Fatto!** Se qualcosa non risponde come previsto, vai a [Se qualcosa non va](#se-qualcosa-non-va).

---

### Facoltativo — Prova dal PC prima di tutto

Se hai Python, puoi verificare account, auto condivisa e risposte **prima** dei passi 4–7:

```
pip install -r lambda/requirements.txt truststore
python prova_locale.py
```

Chiede email e password del nuovo account (non le salva), fa login e lettura dello stato come farà la skill e stampa:

- le frasi che direbbe Alexa, in italiano, inglese e spagnolo;
- il nome dell'auto e i comandi che il cloud le concede;
- le coordinate attuali dell'auto, comode per i `luoghi`.

Non invia comandi all'auto.

---

## Usare la skill

### Frasi che capisce

Non servono le parole esatte, ma queste funzionano di sicuro, dopo *"Alexa, chiedi a my leapcar…"*:

| Per sapere | Frasi |
|---|---|
| Carica | quanto è carica · quanta batteria ha · che autonomia ha · quanti chilometri ha · è in carica · quando finisce la ricarica |
| Posizione | dov'è la macchina · dove si trova · dove l'ho parcheggiata · dove ho lasciato l'auto |
| Anomalie | se è tutto a posto · ci sono anomalie · è chiusa · ho chiuso la macchina · ci sono finestrini aperti · come sono le gomme |
| Tutto | come sta la macchina · fammi un riepilogo · dimmi tutto |
| Chiudere | di chiudere l'auto · di bloccare le portiere · di chiudere i finestrini |
| Clima | di accendere il clima a 21 gradi · di accendere il riscaldamento · di scaldare la macchina a 23 gradi · di accendere l'aria condizionata a 20 · di spegnere il clima |

In inglese e spagnolo le frasi equivalenti sono nei file `en-GB.json` e `es-ES.json`. Dopo ogni risposta la skill si chiude: per un'altra domanda ricomincia con *"Alexa, chiedi a my leapcar…"*.

### Cosa aspettarsi dai comandi

- Alexa ha circa **8 secondi** per rispondere e l'auto a volte ci mette di più a confermare. Se la conferma arriva in tempo senti *«Fatto: l'auto è chiusa a chiave»*, altrimenti *«Ho mandato all'auto il comando di chiusura»*.
- Il cloud Leapmotor risponde "ok" anche quando l'auto ignora un comando: **la conferma vera è chiedere lo stato** un minuto dopo (*"…se è tutto a posto"*).
- Prima di ogni comando la skill legge lo stato: se l'auto è già chiusa o il clima già spento te lo dice e non manda niente. Se l'auto è in movimento non la chiude.
- Se il PIN viene rifiutato la skill **non ritenta**: troppi PIN sbagliati possono bloccare i comandi remoti dell'account.

---

## Aggiornare a una nuova versione

Nelle [note degli aggiornamenti](CHANGELOG.md) ogni versione dice cosa è cambiato e cosa fare. In generale:

- **Se cambia il codice** (quasi sempre): scheda **Code** → **prima copiati da parte il contenuto di `config.json`** → **Import Code** con il nuovo zip → rimetti i tuoi dati in `config.json`, aggiungendo gli eventuali campi nuovi → **Save** → **Deploy**.
  ⚠️ L'import **sovrascrive** `config.json` con i segnaposto: senza la copia, dovresti riscrivere email, password e PIN.
- **Se cambia il modello vocale** (frasi o comandi nuovi): per ogni lingua ricarica il suo `.json` nel JSON Editor e premi **Save**, poi una volta **Build skill**.

Aggiungere le lingue (passo 5a) si fa una volta sola.

---

## Personalizzare

### Il nome della skill

"my leapcar" è il nome con cui si chiama la skill (*invocation name*). Si cambia in **Build → Invocations → Skill Invocation Name**, **in ogni lingua** (la console non lo copia da una all'altra), poi **Build skill**. Regole imparate sul campo:

- **il nome va scritto come lo trascrive l'Echo di quella lingua.** Scritto nell'app Alexa funziona sempre, perché il testo coincide; a voce funziona solo se la trascrizione coincide con il nome. Un Echo in italiano o in spagnolo sente "leapcar" come "lipcar": per questo in `it-IT.json` ed `es-ES.json` il nome è `my lipcar`, mentre in inglese resta `my leapcar`. Se il tuo Echo lo trascrive ancora in un altro modo, **cambia l'invocazione** di conseguenza. Per vedere come l'Echo trascrive la tua pronuncia: app Alexa → *Altro → Impostazioni → Privacy Alexa → Rivedi la cronologia vocale*;

- **almeno due parole**, tutte minuscole;
- **scritte come si pronunciano**: una parola inventata con una grafia che non corrisponde alla pronuncia (*"mylippina"*) non viene riconosciuta;
- **niente nomi di persone famose**: "elettra lamborghini", per esempio, è anche una cantante, e *"Alexa, apri…"* rischia di far partire la sua musica;
- niente "Alexa", "apri", "chiedi", "skill".

Se lo cambi, aggiorna anche `invocationName` nei file `.json`, così un nuovo caricamento non riporta quello vecchio.

### Aggiungere frasi

Se Alexa non capisce una frase che usi spesso, aggiungila tra i `samples` dell'intent giusto nel file della tua lingua (o in *Build → Intents*), poi **Save** e **Build skill**.

### Condividere con la famiglia

Chi usa i tuoi Echo può già usare la skill. Per chi ha **un altro account Amazon** c'è il **beta test** della console (*Distribution → Availability → Beta Test*): fino a 500 persone, nessuna certificazione (ma vanno compilate le schede *Skill Preview* e *Privacy & Compliance*), invito con un link, al massimo **90 giorni** per beta (poi se ne apre un'altra).

Tutti interrogheranno **la tua** auto. Chi ha una sua Leapmotor deve installare una propria copia seguendo questa guida.

---

## Se qualcosa non va

| Sintomo | Causa e rimedio |
|---|---|
| Build: *"Interaction Model does not include Custom Intents"* | Una lingua della skill è senza modello: caricale il suo `.json` (passo 5b), poi rifai **Build skill**. |
| Import Code: *"Your archive's root folder does not contain a lambda folder"* | Lo zip contiene i file sciolti: comprimi la **cartella** `lambda` (passo 3). |
| Alexa: *«Purtroppo non so come aiutarti»* | Non riconosce il nome della skill: modello non compilato (**Build skill**), test non attivo (*Development*), o nome non adatto (vedi *Il nome della skill*). |
| Scritto nell'app Alexa funziona, **a voce no** | L'Echo trascrive il nome in un altro modo. Guarda come lo scrive nella cronologia vocale (app Alexa → *Altro → Impostazioni → Privacy Alexa → Rivedi la cronologia vocale*) e usa proprio quella grafia come nome di quella lingua (vedi *Il nome della skill*). |
| Alexa risponde con l'aiuto a ogni domanda | Nel modello di quella lingua mancano gli intent: ricarica il suo `.json` e rifai la build. |
| *«Si è verificato un problema con la risposta della skill»* | Il codice non parte. Guarda i log: scheda Code → **CloudWatch Logs**, regione *Europe (Ireland)*, log stream più recente. |
| Nei log: `urllib3 v2 only supports OpenSSL 1.1.1+` | `requirements.txt` vecchio: deve contenere `urllib3<2` (il Python di Alexa-hosted usa OpenSSL 1.0.2). |
| Nei log: `JSONDecodeError` | `config.json` non è valido: controlla virgole e virgolette. |
| *«…non è ancora configurata…»* | `config.json` contiene ancora i segnaposto (passo 6). |
| *«Mancano i certificati dell'app…»* | `app.crt` e `app.key` non erano nella cartella `lambda` quando hai fatto lo zip (passo 2). |
| *«Non riesco ad accedere all'account Leapmotor…»* | Email o password sbagliate, oppure account mai aperto nell'app ufficiale (passo 1). |
| *«I comandi sono disattivati…»* / *«…serve il PIN…»* | In `config.json` metti `"comandi": true` e il PIN tra virgolette. |
| *«Il cloud Leapmotor non ha accettato il PIN»* | PIN sbagliato, o l'account della skill non ne ha uno (passo 1.4). Correggilo **prima** di riprovare. |
| *«Leapmotor non consente questo comando…»* | Il cloud non concede quel comando alla tua auto; `prova_locale.py` stampa quelli concessi. |
| *«Il cloud Leapmotor non risponde…»* | Cloud lento o irraggiungibile: riprova. |
| L'app ufficiale sul telefono ti scollega | Stai usando lo stesso account della skill: usa account diversi (passo 1). |
| Prova locale: `CERTIFICATE_VERIFY_FAILED` sull'indirizzo | Un antivirus che ispeziona l'HTTPS (per esempio Norton): installa `truststore`. Su Amazon il problema non c'è. |

---

## Come funziona

Alexa non parla col telefono: a ogni domanda Amazon esegue la funzione Python della skill, che fa login al cloud Leapmotor con TLS mutuo (certificato dell'app, poi certificato dell'account), legge lo stato dell'auto e risponde nella lingua dell'Echo. La sessione resta aperta finché Amazon tiene in vita la funzione, quindi le domande ravvicinate non rifanno il login; una lettura richiede in genere meno di un secondo. L'indirizzo arriva da OpenStreetMap (Nominatim), gratis e senza chiave.

| File | Cosa fa |
|---|---|
| `lambda/lambda_function.py` | gestori Alexa: domande, comandi, aiuto, errori |
| `lambda/leapcloud.py` | login mTLS, elenco veicoli, lettura stato, invio comandi |
| `lambda/comandi.py` | cosa mandare all'auto per ogni comando; niente rete, si prova offline |
| `lambda/risposte.py` | lettura dello stato e scelta della frase; niente rete, si prova offline |
| `lambda/lingua_it.py`, `lingua_en.py`, `lingua_es.py` | le frasi, una lingua per file, tutte con le stesse funzioni |
| `lambda/lingue.py`, `lambda/comune.py` | scelta della lingua dal locale dell'Echo; pezzi comuni alle lingue |
| `lambda/posizione.py` | indirizzo dalle coordinate |
| `lambda/config.json` | credenziali, comandi e luoghi (nel repository solo segnaposto) |
| `skill-package/interactionModels/custom/*.json` | modelli vocali, uno per lingua |
| `prova_locale.py` | prova dal PC con l'account vero |
| `crea_zip.py` | crea lo zip da importare |
| `test/test_offline.py` | crittografia contro i vettori di riferimento, frasi e comandi nelle tre lingue su uno stato reale della T03 |

Test: `python -m pytest test` (o `python test/test_offline.py`).

## Crediti

Il protocollo del cloud Leapmotor è stato ricostruito da altri, e il merito è loro:

- [**markoceri/leapmotor-api**](https://github.com/markoceri/leapmotor-api): libreria Python del protocollo (firme, HKDF, SM4), da cui deriva `leapcloud.py`.
- [**markoceri/leapmotor-certs**](https://github.com/markoceri/leapmotor-certs): certificati TLS dell'app.
- [**ProtossBlaster/leapmotor-mate**](https://github.com/ProtossBlaster/leapmotor-mate): verifiche sul campo dei segnali di stato.

## Licenza

[GNU AGPL-3.0](LICENSE), la stessa di leapmotor-api da cui il codice deriva.
