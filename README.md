# Leapmotor per Alexa

Skill Alexa **personale**, in italiano, per chiedere a voce lo stato della tua Leapmotor e darle qualche comando:

| Chiedi | Alexa risponde |
|---|---|
| *"Alexa, chiedi a mia lippina **quanto è carica**"* | «La batteria è all'81 per cento, circa 218 chilometri di autonomia.» Se è in carica aggiunge quanto manca e fino a che percentuale. |
| *"Alexa, chiedi a mia lippina **dov'è la macchina**"* | «L'auto si trova in Piazza Maggiore 1, a Bologna.» Oppure «L'auto è a casa», se configuri i tuoi luoghi. Nell'app Alexa arriva anche il link alla mappa. |
| *"Alexa, chiedi a mia lippina **se è tutto a posto**"* | Portiere, finestrini, baule, gomme, e se l'auto ferma non è chiusa a chiave. |
| *"Alexa, **apri** mia lippina"* | Tutte e tre le cose insieme, compreso se il clima è acceso. |
| *"Alexa, chiedi a mia lippina di **chiudere l'auto**"* | La chiude a chiave (se è ferma e non è già chiusa). |
| *"Alexa, chiedi a mia lippina di **chiudere i finestrini**"* | Li chiude, se ce n'è uno aperto. |
| *"Alexa, chiedi a mia lippina di **accendere il riscaldamento a 22 gradi**"* | Anche *aria condizionata*, oppure solo *il clima*: allora sceglie caldo o freddo in base alla temperatura esterna. Temperature da 18 a 32 gradi. |
| *"Alexa, chiedi a mia lippina di **spegnere il clima**"* | Lo spegne. |

Se l'auto non si fa sentire dal cloud da più di 6 ore, Alexa dice quando è stato l'ultimo contatto.

> **Niente aperture.** I comandi si attivano solo se lo decidi tu in `config.json`, e anche così la skill può soltanto **chiudere** l'auto e i finestrini e comandare il clima. Aprire l'auto o i finestrini non è previsto, di proposito: una skill vocale la può usare chiunque sia nella stanza, compresa la TV.

> **Progetto non ufficiale**, senza alcun rapporto con Leapmotor o Amazon. Usa API del cloud Leapmotor non documentate, che possono cambiare senza preavviso. Provato su una **Leapmotor T03**; il codice legge anche il formato di stato di C10/B10, ma su quei modelli non è stato verificato.

Cosa è cambiato tra una versione e l'altra: [note degli aggiornamenti](CHANGELOG.md).

La skill resta in **modalità sviluppo** sul tuo account Amazon: non serve pubblicarla né farla certificare, e funziona su tutti i tuoi Echo e nell'app Alexa.

---

## Cosa serve

- Un account **Amazon** (lo stesso dei tuoi Echo) e un account sviluppatore Amazon: è gratuito e si attiva al primo accesso alla console.
- Un **account Leapmotor dedicato alla skill** (vedi passo 1).
- I **certificati dell'app** Leapmotor (passo 2).
- Facoltativo: **Python 3** sul PC, per la prova locale e per creare lo zip con un comando.

## 1. Un account Leapmotor solo per la skill

Il cloud Leapmotor tiene **una sola sessione per account**. Se la skill usasse l'account con cui entri nell'app ufficiale, vi buttereste fuori a vicenda.

1. Crea un nuovo account Leapmotor con un'altra email.
2. Dall'account proprietario **condividi l'auto** con il nuovo account.
3. Entra **una volta** nell'app ufficiale con il nuovo account: accetta i termini e controlla che l'auto compaia.
4. Solo se vuoi i comandi: sempre con il nuovo account, imposta nell'app il **PIN dei comandi remoti** e prova un comando qualunque, per essere sicuro che quell'account li possa dare.
5. Esci. Da qui in avanti quell'account lo usa solo la skill.

## 2. Scarica il progetto e i certificati

1. Scarica questo progetto: pulsante verde **Code → Download ZIP**, poi estrai l'archivio.
2. Scarica i due file `app.crt` e `app.key` da **<https://github.com/markoceri/leapmotor-certs>**. Sono i certificati TLS dell'app ufficiale, estratti dal progetto leapmotor-api; qui non vengono ridistribuiti.
3. Mettili nella cartella `lambda` del progetto, accanto a `lambda_function.py`.

## 3. Prova dal PC (facoltativa, consigliata)

Verifica credenziali, auto condivisa e tempi di risposta prima di toccare Amazon:

```
pip install -r lambda/requirements.txt truststore
python prova_locale.py
```

Lo script chiede email e password del nuovo account senza salvarle, e stampa le frasi che direbbe Alexa, il nickname dell'auto e i comandi che il cloud le concede. Non invia comandi. Stampa anche le coordinate attuali dell'auto, comode per configurare i luoghi (passo 6).

## 4. Crea lo zip del codice

Con Python:

```
python crea_zip.py
```

Crea `leapmotor-alexa-lambda.zip` e si ferma con un messaggio se mancano i certificati.

**Senza Python (Windows):** tasto destro sulla cartella `lambda` → *Comprimi in file ZIP* (oppure *Invia a → Cartella compressa*). Lo zip deve contenere **la cartella `lambda`**, non i file sciolti: altrimenti la console risponde *"Your archive's root folder does not contain a lambda folder"*.

## 5. Crea la skill nella console Alexa

Vai su <https://developer.amazon.com/alexa/console/ask> **con lo stesso account Amazon degli Echo** e clicca **Create Skill**:

1. **Name, Locale**: nome a piacere, lingua **Italian (IT)**. Poi *Next*.
2. **Experience, Model, Hosting service**:
   - *Choose a type of experience*: **Other**
   - *Choose a model*: **Custom**
   - *Hosting services*: **Alexa-hosted (Python)**
   - *Hosting region*: **EU (Ireland)**

   Poi *Next*.
3. **Templates**: **Start from Scratch** → *Next* → **Create Skill**. Aspetta un paio di minuti.

### Modello vocale (scheda **Build**)

1. A sinistra apri **Interaction Model** → **JSON Editor**.
2. Trascina il file `skill-package/interactionModels/custom/it-IT.json`.
3. **Save**, poi **Build skill**, e aspetta *Build Successful*.
4. Controlla che a sinistra, sotto *Intents*, ci siano tutti: **BatteriaIntent**, **PosizioneIntent**, **AnomalieIntent**, **RiepilogoIntent**, **ChiudiAutoIntent**, **ChiudiFinestriniIntent**, **ClimaIntent**, **RiscaldamentoIntent**, **RaffreddamentoIntent** e **SpegniClimaIntent**. Se mancano, Alexa risponde con l'aiuto: ricarica il JSON e rifai la build.

## 6. Carica il codice e configura (scheda **Code**)

1. **Import Code** → scegli lo zip del passo 4 → seleziona tutti i file → **Import**. Se chiede di sovrascrivere `lambda_function.py` e `requirements.txt`, conferma.
2. Apri `lambda/config.json` nell'editor della console e compila:

```json
{
  "email": "email-dell-account-della-skill@esempio.it",
  "password": "la-sua-password",
  "vin": "",
  "nome": "",
  "comandi": false,
  "pin": "",
  "ventola": 3,
  "luoghi": [
    { "nome": "a casa", "lat": 44.493889, "lon": 11.342778, "raggio_m": 150 },
    { "nome": "in ufficio", "lat": 0.0, "lon": 0.0, "raggio_m": 150 }
  ]
}
```

| Campo | A cosa serve |
|---|---|
| `email`, `password` | l'account Leapmotor del passo 1 |
| `vin` | solo se sull'account ci sono più auto; vuoto = la prima |
| `nome` | facoltativo: come Alexa chiama l'auto nelle risposte («Elettra Lamborghini è chiusa a chiave») e nella scheda. Vuoto = il nome dato all'auto nell'app ufficiale; se non c'è neanche quello, «l'auto» |
| `comandi` | `true` per abilitare chiusura e clima, `false` (predefinito) per una skill di sola lettura |
| `pin` | il PIN dei comandi remoti del nuovo account (passo 1.4), tra virgolette: `"1234"`. Serve solo con `comandi: true` |
| `ventola` | velocità della ventola quando Alexa accende il clima, da 1 a 7 |
| `luoghi` | facoltativo. Se l'auto è entro `raggio_m` metri, Alexa dice il `nome` («L'auto è a casa») invece dell'indirizzo. Il nome viene letto così com'è: «a casa», «in ufficio», «dai nonni». Le voci con coordinate 0,0 vengono ignorate. |

Attenzione a virgole e virgolette: un errore di sintassi blocca la skill all'avvio. Se la password contiene `"` scrivila come `\"`.

3. **Save** → **Deploy**. Il deploy dura circa un minuto, perché Amazon installa le librerie.

> Le credenziali restano nel repository privato che Amazon crea per la skill, visibile solo al tuo account sviluppatore. Non mettere mai la password nel `config.json` del progetto se poi lo pubblichi.

## 7. Prova e usa

Scheda **Test** → in alto imposta *Skill testing is enabled in* su **Development** → scrivi, **senza "Alexa"** davanti:

```
chiedi a mia lippina quanto è carica
```

Poi prova a voce su un Echo. Non devi attivare niente: le skill in sviluppo sono già attive sul tuo account. Nell'app Alexa la trovi in *Altro → Skill e giochi → Le tue skill → Sviluppatore*.

### Frasi che capisce

Non servono le parole esatte, ma queste funzionano di sicuro (dopo *"Alexa, chiedi a mia lippina…"*):

| Per sapere | Frasi |
|---|---|
| Carica | quanto è carica · quanta batteria ha · che autonomia ha · quanti chilometri ha · è in carica · quando finisce la ricarica |
| Posizione | dov'è la macchina · dove si trova · dove l'ho parcheggiata · dove ho lasciato l'auto |
| Anomalie | è tutto a posto · ci sono anomalie · è chiusa · ho chiuso la macchina · ci sono finestrini aperti · come sono le gomme |
| Tutto | come sta la macchina · fammi un riepilogo · dimmi tutto |
| Chiudere | chiudi l'auto · blocca le portiere · chiudi i finestrini · alza i finestrini |
| Clima | accendi il clima a 21 gradi · accendi il riscaldamento · scalda la macchina a 23 gradi · accendi l'aria condizionata a 20 · rinfresca l'auto · spegni il clima |

Vanno bene anche con l'infinito: *"…chiedi a mia lippina di chiudere l'auto"*.

Dopo ogni risposta la skill si chiude: per un'altra domanda ricomincia con *"Alexa, chiedi a…"*.

### Cosa aspettarsi dai comandi

- Alexa ha circa **8 secondi** per rispondere, e l'auto a volte impiega di più per confermare. Se la conferma arriva in tempo senti *«Fatto: l'auto è chiusa a chiave»*, altrimenti *«Ho mandato all'auto il comando di chiusura»*.
- Il cloud Leapmotor risponde "ok" anche quando l'auto ignora un comando. **La conferma vera è chiedere lo stato** un minuto dopo: *"…è tutto a posto?"* dice se è chiusa, se ci sono finestrini aperti e se il clima è acceso.
- Prima di ogni comando la skill legge lo stato: se l'auto è già chiusa o il clima già spento te lo dice e non manda niente. Se l'auto è in movimento non la chiude.
- Se il PIN viene rifiutato la skill **non ritenta**: troppi PIN sbagliati possono bloccare i comandi remoti dell'account.

---

## Personalizzare

### Il nome della skill

"mia lippina" è il nome con cui si chiama la skill (*invocation name*). Puoi cambiarlo in **Build → Invocations → Skill Invocation Name**, poi **Save** e **Build skill**. Qualche regola imparata sul campo:

- **Almeno due parole**, tutte minuscole.
- **Parole italiane, scritte come si pronunciano.** Alexa confronta il nome con quello che sente, trascritto in italiano: *"my leap car"* non viene riconosciuto, e *"mylippina"* (una parola, grafia inglese) nemmeno.
- Niente "Alexa", "apri", "chiedi", "skill".

Se cambi nome, aggiorna anche `invocationName` in `it-IT.json`, così alla prossima importazione del modello non torna quello vecchio.

### Aggiungere frasi

Se Alexa non capisce una frase che usi spesso, aggiungila tra i `samples` dell'intent giusto in `it-IT.json` (oppure in *Build → Intents*), poi **Save** e **Build skill**.

### Aggiornare il codice

**Reimportare lo zip sovrascrive `config.json`** con i segnaposto, e dovresti riscrivere email e password. Per una modifica piccola conviene aprire il file nella scheda Code, incollare la nuova versione, poi **Save** e **Deploy**.

Per passare a una versione nuova del progetto:
1. ricarica il modello vocale (`it-IT.json` nel JSON Editor, **Save**, **Build skill**);
2. prima di importare, **copiati da parte** il `config.json` attuale dalla console;
3. reimporta lo zip e rimetti i tuoi dati nel nuovo `config.json`, aggiungendo i campi nuovi se ce ne sono;
4. **Save** → **Deploy**.

## Condividere con la famiglia

Chi usa i tuoi Echo può già interrogare la skill. Per darla anche a chi ha **un altro account Amazon** c'è il **beta test** della console (*Distribution → Availability → Beta Test*):

- fino a 500 persone, ognuna col proprio account Amazon;
- nessuna certificazione, ma vanno compilate le schede *Skill Preview* (nomi, descrizioni, icone) e *Privacy & Compliance*;
- mandi tu il link di invito e loro attivano la skill dall'app Alexa;
- ogni beta dura al massimo **90 giorni**; poi se ne può aprire un'altra.

Tutti interrogheranno **la tua** auto: le credenziali sono una sola, in `config.json`. Chi ha una sua Leapmotor deve creare la propria copia della skill seguendo questa guida.

---

## Se qualcosa non va

| Sintomo | Causa e rimedio |
|---|---|
| Alexa: *«Purtroppo non so come aiutarti»* | Non riconosce il nome della skill: modello non compilato (*Build skill*) o nome non adatto (vedi *Il nome della skill*). |
| Alexa risponde con l'aiuto a ogni domanda | Nel modello mancano gli intent: ricarica `it-IT.json` nel JSON Editor e rifai la build. |
| *«Si è verificato un problema con la risposta della skill»* | Il codice non parte. Guarda i log: scheda Code → **CloudWatch Logs**, regione *Europe (Ireland)*, log stream più recente. |
| Nei log: `urllib3 v2 only supports OpenSSL 1.1.1+` | `requirements.txt` vecchio. Deve contenere `urllib3<2`, perché il Python di Alexa-hosted usa OpenSSL 1.0.2. |
| Nei log: `JSONDecodeError` | `config.json` non è JSON valido (virgola o virgoletta). |
| *«…non è ancora configurata…»* | `config.json` contiene ancora i segnaposto. |
| *«I comandi sono disattivati…»* / *«…serve il PIN…»* | In `config.json` metti `"comandi": true` e il PIN tra virgolette. |
| *«Il cloud Leapmotor non ha accettato il PIN»* | PIN sbagliato, o l'account della skill non ha un PIN per i comandi (passo 1.4). Correggilo **prima** di riprovare. |
| *«Leapmotor non consente questo comando…»* | Il cloud non concede quel comando alla tua auto. `prova_locale.py` stampa i comandi concessi. |
| *«Mancano i certificati dell'app…»* | `app.crt` e `app.key` non sono nella cartella `lambda` dello zip (passo 2). |
| *«Non riesco ad accedere all'account Leapmotor…»* | Email o password sbagliate, oppure account mai usato nell'app ufficiale (passo 1). |
| *«Il cloud Leapmotor non risponde…»* | Cloud lento o irraggiungibile: riprova. |
| Prova locale: errore `CERTIFICATE_VERIFY_FAILED` sull'indirizzo | Un antivirus che ispeziona l'HTTPS (per esempio Norton). Installa `truststore` (passo 3). Su Amazon il problema non c'è. |

---

## Come funziona

Alexa non parla col telefono: a ogni domanda Amazon esegue la funzione Python della skill, che fa login al cloud Leapmotor con TLS mutuo (certificato dell'app, poi certificato dell'account), legge lo stato dell'auto e compone la risposta. La sessione resta aperta finché Amazon tiene in vita la funzione, quindi le domande ravvicinate non rifanno il login. Una lettura richiede in genere meno di un secondo; Alexa concede circa 8 secondi.

L'indirizzo si ricava da OpenStreetMap (Nominatim), gratis e senza chiave.

| File | Cosa fa |
|---|---|
| `lambda/lambda_function.py` | gestori Alexa: domande, comandi, aiuto, errori |
| `lambda/leapcloud.py` | login mTLS, elenco veicoli, lettura stato, invio comandi |
| `lambda/comandi.py` | cosa mandare all'auto e cosa rispondere; niente rete, si prova offline |
| `lambda/risposte.py` | dallo stato alle frasi italiane; niente rete, si prova offline |
| `lambda/posizione.py` | indirizzo dalle coordinate |
| `lambda/config.json` | credenziali e luoghi (solo segnaposto nel repository) |
| `skill-package/…/it-IT.json` | modello vocale: nome della skill e frasi |
| `prova_locale.py` | prova dal PC con l'account vero |
| `crea_zip.py` | crea lo zip da importare |
| `test/test_offline.py` | crittografia contro i vettori di riferimento, frasi e comandi su uno stato reale della T03 |

Test: `python test/test_offline.py` (o `python -m pytest test`).

## Crediti

Il protocollo del cloud Leapmotor è stato ricostruito da altri, e il merito è loro:

- [**markoceri/leapmotor-api**](https://github.com/markoceri/leapmotor-api): libreria Python del protocollo (firme, HKDF, SM4), da cui deriva `leapcloud.py`.
- [**markoceri/leapmotor-certs**](https://github.com/markoceri/leapmotor-certs): certificati TLS dell'app.
- [**ProtossBlaster/leapmotor-mate**](https://github.com/ProtossBlaster/leapmotor-mate): verifiche sul campo dei segnali di stato.

## Licenza

[GNU AGPL-3.0](LICENSE), la stessa di leapmotor-api da cui il codice deriva.
