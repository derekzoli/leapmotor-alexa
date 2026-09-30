# Note degli aggiornamenti

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
