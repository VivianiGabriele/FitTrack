# FitTrack
Link Railway: web-production-9f5e4.up.railway.app

Progetto di una fitness_app chiamata FitTrack per il secondo elaborato di PPM

Il sito funziona in questo modo, sono implementate funzionalità di log in, sing in, cambio password, reset password, log out, durante la registrazione si può scegliere tramite form se essere un utente normale (atleta) oppure un coach.
In alto a destra c'è la sezione profilo, settings e log out,in Profile si hanno tutti i dati personali, e con la funzionalità che i dati non sono modificabili a meno che non si prema il pulsante Edit Profile, il settings al momento non fa niente ma l'ho lasciato per implementazioni future, per poter cambiare le impostazioni generali della pagina come lingua, privacy etc..

Se non si è effettuato il login, le pagine Workouts e Goals faranno un redirect a Login.

Effettuato il cambio password l'utente dovrà rifare il login.

Una volta registrati tornati all'home page si può accedere alla pagina dei workouts, in cui sia coach che atleti potranno registrare ogni giorno il workout svolto.

Stessa cosa vale per la pagina Goals, ovvero sia coach che atleti possono registrare i loro obiettivi nel tempo (peso, massa grassa, etc etc..) e anche le misurazioni, che servono per tenere traccia durante il percoso 
del proprio peso, massa grassa etc etc.. in alto alla pagina si avrà un grafico raffigurante le misurazioni della settimana in corso, uno rafficura il peso e uno la massa grassa. così da avere un riscontro grafico del percorso che si sta svolgendo.
I coach hanno una pagina dedicata solo per loro Coach Dashboard, in cui, per facilità un coach può scegliere tramite un form di assegnarsi un atleta, avevo inizialmente pensato di fare un applicativo per le palestre così che i coach di palestra potessero tenere 
sotto controllo gli atleti, nella pagina si avrà una lista di atleti seguiti, si può entrare nel profilo di ognuno attraverso view stats, oppure rimuoverlo, di ogni'atleta il coach sarà in grado di vedere i workouts, i goals e anche le misurazioni, inoltre sarà possibile per il coach commentare le misurazioni dell'atleta, può fare commento visibile anche all'atleta (o solo ai coach
supponendo ci siano più coach a seguirlo o anche nutrizionisti oprofessionisti di altro tipo)
L'atleta nella pagina goals vedrà in basso i commenti lasciti dai coach per le relative misurazioni.

Nella home in basso si hanno anche delle tabelle che mostrano un recap degli ultimi workouts e goals.
Ho implementato pure attraverso middlewere la fuonzionalità del reminder, ovvero quando un utente ha registrato almeno un workout, se non dovesse più registrarne altri, dopo una settimana, effettuato il log in, avrà in alto nella home (e in tutte le altre pagine del sito)
un piccolo remainder che lo invita ad aggiungere dei workout giornalieri.

Ecco le credenziali di alcuni utenti per fare i test:
Atleti:

Username: GabrieleViviani
Password: Gabviv1234!

Username: AsiaDelogu
Password: Asia1234!

Coach:
Username: GianzCoach
Password: Gianz1234!

Le consiglio però di provare lei a registrare un utente, magari coach, gli assegna un atleta, e attraverso la pagina Coach Dashboard osservare i workouts/goals/misurations e commentare una misuration
