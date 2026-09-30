# Note degli aggiornamenti

## 1.2.1 — 30 settembre 2026

- **Guide di installazione in inglese e spagnolo**: [README.en.md](README.en.md) e [README.es.md](README.es.md), con le risposte e i messaggi d'errore che Alexa dice davvero in quella lingua.
- Modello spagnolo: aggiunte *"si hay ventanillas abiertas"*, *"si hay alguna ventanilla abierta"*, *"si hay alguna puerta abierta"*. Per averle, ricarica `es-ES.json` nel JSON Editor della lingua spagnola → **Save** → **Build skill**. Il codice non cambia.

## 1.2 — 30 settembre 2026

### Novità

- **Tre lingue: italiano, inglese e spagnolo.** È la stessa skill con più lingue nella console Alexa: il codice è uno solo e risponde nella lingua dell'Echo che la interroga. Domande, comandi e regole di sicurezza sono identici in tutte e tre.
  - **Inglese** (modelli `en-GB.json` e `en-US.json`): chilometri e gradi Celsius. *"Alexa, ask my leapcar how much charge it has"*, *"…to lock the car"*, *"…to turn on the heating to 21 degrees"*.
  - **Spagnolo** (modello `es-ES.json`): *"Alexa, pregunta a my leapcar dónde está el coche"*, *"Alexa, pide a my leapcar que cierre el coche"*.
  - Anche gli indirizzi arrivano nella lingua giusta ("Bologna" / "Bolonia").
- **Nuovo nome della skill: "my leapcar"**, uguale in tutte le lingue.
- **Luoghi con un nome per lingua**: `"nome": { "it": "a casa", "en": "at home", "es": "en casa" }`. Un nome semplice continua a valere per tutte le lingue.
- **Nuovo campo `fuso_orario`** in `config.json` (1 = Italia e Spagna, 0 = Regno Unito) per dire l'ora giusta dell'ultimo contatto con l'auto.
- `prova_locale.py` stampa le risposte in tutte e tre le lingue.

### Sotto il cofano

- Le frasi sono in `lingua_it.py`, `lingua_en.py`, `lingua_es.py`, con le stesse funzioni. Stato, sicurezza dei comandi e messaggi mandati all'auto sono in comune: non cambiano con la lingua.
- Le frasi italiane sono rimaste identiche alla 1.1 (verificato dai test).

### Come aggiornare dalla 1.1

1. **Code**: copiati da parte il tuo `config.json`, **Import Code** con il nuovo zip, poi rimetti i tuoi dati (e, se vuoi, `fuso_orario` e i nomi dei luoghi per lingua). **Save** → **Deploy**.
2. **Build**, per l'italiano: ricarica `it-IT.json` (cambia solo il nome della skill) → **Save** → **Build skill**.
3. Per le lingue nuove: *Language settings* → aggiungi *English (UK)*, *English (US)*, *Spanish (ES)*; per ognuna carica il suo `.json` e fai **Build skill** (vedi il README).

## 1.1 — 30 settembre 2026

### Novità

- **Comandi vocali**, da attivare in `config.json` con `"comandi": true` e il PIN dei comandi remoti:
  - *"…chiudi l'auto"*: la chiude a chiave. Se è già chiusa lo dice e non manda niente; se è in movimento non la chiude.
  - *"…chiudi i finestrini"*.
  - *"…accendi il riscaldamento / l'aria condizionata a 22 gradi"*, oppure solo *"…accendi il clima"*: in quel caso sceglie caldo o freddo in base alla temperatura esterna. Temperature da 18 a 32 gradi, 22 se non la dici.
  - *"…spegni il clima"*. Per la T03 usa lo spegnimento completo verificato sull'auto (lo stesso accolto in leapmotor-mate 3.10.0).
  - Funzionano anche le frasi con l'infinito: *"…chiedi a mia lippina **di** chiudere l'auto"*.
- **Aprire l'auto o i finestrini non è previsto, di proposito**: una skill vocale la può usare chiunque sia nella stanza, compresa la TV.
- **Il clima nello stato**: *"…è tutto a posto?"* e il riepilogo dicono se il clima è acceso e a che temperatura.
- **Il nome dell'auto nelle risposte**: la skill legge il nome dato all'auto nell'app ufficiale e lo usa al posto di «l'auto» (*«Elettra Lamborghini è chiusa a chiave»*). Si può sostituire con il campo `nome` in `config.json`. Un nome scritto tutto attaccato ("ElettraLamborghini") viene diviso, altrimenti Alexa lo legge male. Nel riepilogo il nome compare una volta sola, all'inizio.
- **Il riepilogo parte dalla posizione**: *«… si trova in Piazza Maggiore 1, a Bologna. La batteria è …»*.
- `prova_locale.py` stampa anche il nome dell'auto, i comandi che il cloud le concede e salva l'elenco veicoli completo in `ultimo_elenco_veicoli.json`. Il file resta sul PC ed è escluso da git.

### Sicurezza dei comandi

- Alexa aspetta la conferma dell'auto per circa 6 secondi. Se arriva risponde *«Fatto»*, altrimenti *«Ho mandato …»*. Il cloud Leapmotor risponde "ok" anche quando l'auto ignora un comando, quindi la conferma vera è chiedere lo stato un minuto dopo.
- Se il PIN viene rifiutato la skill **non ritenta**: troppi PIN sbagliati possono bloccare i comandi remoti dell'account.
- Prima di ogni comando la skill controlla che la tua auto lo consenta (`rightList` del cloud) e altrimenti lo dice.
- Firme e cifratura del PIN sono verificate carattere per carattere contro markoceri/leapmotor-api.

### Correzioni

- Il nome dell'auto si legge da `vinNickname`: `nickName` è il nickname dell'**utente**, non dell'auto.
- Frase sgrammaticata quando l'indirizzo non si trova e l'auto è in movimento.

### Come aggiornare dalla 1.0

1. **Build** → JSON Editor: carica il nuovo `it-IT.json` → **Save** → **Build skill**. Sotto *Intents* devono comparire anche ChiudiAuto, ChiudiFinestrini, Clima, Riscaldamento, Raffreddamento e SpegniClima.
2. **Code**: copiati da parte il tuo `config.json`, poi **Import Code** con il nuovo zip (`python crea_zip.py`).
3. Rimetti i tuoi dati in `config.json` e aggiungi i campi nuovi: `nome`, `comandi`, `pin`, `ventola` (vedi il README).
4. **Save** → **Deploy**.

## 1.0 — 28 settembre 2026

Prima versione: skill Alexa in italiano, in sola lettura.

- *"…quanto è carica"*: percentuale, chilometri di autonomia e, se è in carica, quanto manca e fino a che percentuale.
- *"…dov'è la macchina"*: indirizzo da OpenStreetMap, oppure un luogo configurato («a casa»), con il link alla mappa nell'app Alexa.
- *"…è tutto a posto?"*: portiere, finestrini, baule, gomme, chiusura a chiave a veicolo fermo.
- *"Alexa, apri mia lippina"*: tutto insieme.
- Se l'auto non si fa sentire da più di 6 ore, Alexa dice quando è stato l'ultimo contatto.
- Compatibile con il runtime Alexa-hosted (Python con OpenSSL 1.0.2: `urllib3<2`, TLS 1.2).
