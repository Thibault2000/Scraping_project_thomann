# Traitement & Analyse de données de site E-commerce
Pour ce projet, nous avons choisi de travailler sur le site Thomann, leader européen de la vente 
d'instruments de musique. Au-delà de nos affinités personnelles, ce choix repose sur trois 
critères techniques identifiés lors de nos tests de sites :  

- L'accessibilité technique : Contrairement à d'autres plateformes de e-commerce, le site 
n'est pas "bloqué" par des systèmes de protection, ce qui permet l'extraction de données.   
- Une arborescence riche mais cohérente : Le site présente une structure complexe 
(plusieurs niveaux de sous-catégories) mais "propre" (pas de catégories invisibles). 
- La Stabilité des données : Nos analyses de pages-tests ont montré une structure HTML 
constante d'un instrument à l'autre, facilitant l'automatisation de l'extraction.

Cependant le catalogue complet de Thomann représente plus de 160 000 articles de références. 
Une extraction totale aurait nécessité plus de 48 heures d'exécution, augmentant les risques de 
bannissement d'adresse IP et générant une base de données brute d'environ 25 Go (la collecte 
de notre base de données quant à elle pèse 3,8 go).  
Afin d'éviter un processus trop long, risqué et coûteux en stockage, nous avons ciblé la catégorie 
"Instruments à claviers". Malgré ce ciblage, le script a fonctionné durant 9 heures consécutives 
(une nuit complète) pour extraire environ 9 000 fiches produits. 
Pour constituer notre base de données nous avons divisé en 2 scripts python. Le premier est 
chargé de reproduire l'arborescence et de récupérer l'intégralité des fichiers HTML et le second 
nous sert à constituer la base de données.

## Extraction de données
### Organisation du script
Avant de lancer la récupération des données, nous avons coupé notre script en plusieurs phases. 
Cette division répond à un besoin de sécurité et de visibilité : en isolant chaque étape, nous 
pouvons valider la structure des dossiers avant de lancer le processus le plus lourd et long. Cela 
nous a également permis de tester la réaction du site face à nos requêtes sur des durées plus 
courtes. 
#### Configuration et outils de préparation 
La première étape consiste à préparer l'environnement de travail. Pour cela nous avons : 
- Identifié que les adresses du site suivent une structure précise (https://www.thomann.fr/ 
+ nom_de_la_page.html). Nous avons donc configuré une URL de base pour 
reconstruire tous les liens du site par la suite. 
- Créé deux fonctions, une dédiée au nettoyage des noms afin d’éviter que certain 
caractère spécial ne fasse bugger notre chemin. Et un second analysant automatique du 
type de page. Nous avons divisé les pages en 2 catégories : les pages « catégorie » et les 
pages « produits ».

#### La récupération de donnée

Cette phase est le cœur du projet et se déroule en trois temps :  

- Initialisation des catégories de base : Le script identifie d'abord les premières grandes 
sections et leur crée des fichiers pour poser les fondations de notre base de données 
locale.
- Création de l’architecture du site sur notre ordinateur : python explore les sous
catégories qui s'imbriquent les unes dans les autres pour créer l'arborescence des 
dossiers. Cette étape est importante car elle ne dure que 10 minutes environ. C'est 
« l’ultime » moment de vérification : si les dossiers sont correctement créés à ce stade, 
nous savons que la logique de navigation est validée. 
- Téléchargement des fiches produits : Une fois le plan du site reproduit sur notre 
ordinateur, nous lançons la phase la plus longue : la récupération de l'intégralité des 
pages HTML des instruments. 

#### Analyse post-extraction  
Une fois le téléchargement terminé, une dernière phase intervient pour s'assurer qu'aucune 
donnée n'a été oubliée à cause d'un micro-bug réseau :

- Identification des anomalies : Le script scanne les dossiers et utilise nos fichiers témoins 
(scrapping_fait.txt) pour repérer les catégories présentant un problème. Si un dossier est 
jugé incomplet, le témoin est supprimé. 
- Relance ciblée : Grâce à notre gestion des dossiers déjà existants et à l'attribution de 
numéros uniques pour chaque produit, nous pouvons relancer le script de récupération 
uniquement sur les zones manquantes. Le script complète alors les "trous" sans jamais 
retélécharger ce qui est déjà présent sur le disque.

### Obstacles rencontrés et solutions techniques
Le succès de notre extraction de 9 heures repose sur l'anticipation des erreurs. Nous avons mis 
en place plusieurs mécanismes pour que le script soit capable de gérer seul les imprévus 
identifiés. 
#### Camouflage (Anti-Scraping) 
Lors de notre seconde phase (création de l’architecture), nous avons été confrontés à un 
bannissement temporaire. Le serveur nous a détectés comme un robot et a bloqué nos requêtes. 
Cet incident nous a permis d'ajuster notre stratégie pour l'extraction longue :

- Temporisation (Random Sleep) : Nous avons imposé une pause aléatoire de 3 à 5 
secondes entre chaque requête. Ce délai casse la régularité du script et imite une 
navigation humaine, ce qui est suffisant pour éviter l'erreur 429 sans trop rallonger la 
durée totale. 
- Gestion automatique de l'erreur 429 : Si le serveur signale malgré tout une saturation, 
le script intercepte l'erreur et impose une pause de 60 secondes pour se faire "oublier" 
avant de reprendre le travail.

#### Anticipation des erreurs d'URLs  
Pour éviter les blocages, nous testons systématiquement chaque URL avec 
« .startswith("https" ) ». Si le lien récupéré n'est pas complet, on utilise « .lstrip("/") » avant 
d'ajouter l’URL de « base ». Cette précaution garantit de ne jamais créé de chemins invalides 
(comme une double adresse collée ou un double slash au milieu). 

#### Gestion des instabilités réseau  
Le web et les connexions Wi-Fi domestiques étant par nature instables, nous avons intégré un 
système de 3 tentatives. Pour chaque téléchargement, le script ne s’arrête pas en cas d'échec : il 
affiche l'erreur, attend quelques secondes et réessaie. Ce n'est qu'après trois échecs consécutifs 
qu'il passe au produit suivant pour ne pas rester bloqué indéfiniment. 

#### Contrôle et suivi du processus 
Comme le script tourne en autonomie, nous utilisons des print stratégiques pour surveiller 
l'avancement. Pour les produits, un modulo permet d'afficher un message de succès tous les 5 
téléchargements (ex: 1/50 ok, 6/50 ok). Cela permet de vérifier d'un coup d'œil que le processus 
suit son cours. 

#### Contraintes système (Windows) et nommage des fichiers 
Nous avons dû gérer une contrainte matérielle importante : la limite de 256 caractères pour les 
chemins de dossiers sur Windows. Pour éviter de dépasser ce seuil, nous avons remplacé le nom 
commercial (ex : Yamaha GB1 K Black Polished) par un identifiant générique : Item_1, Item_2, 
etc. Ce choix présente trois avantages :

- Traçabilité : Chaque fichier est lié à son ordre d'apparition. L'article n°35 sera nommé 
Item_36.html (index +1 pour éviter l'Item_0). Ce numéro reste fixe, même si l'article 
précédent échoue. 
- Continuité : Si le script s'arrête en milieu de catégorie, il peut être relancé sans créer de 
doublons. 
- Correction d’erreur : S'il manque une ou deux fiches dans un dossier de 60 produits, le 
script identifie les numéros manquants et télécharge uniquement les éléments restants 
après suppression du fichier témoin.

#### Fichiers témoins  
Les fichiers témoins servent de "mémoire" au projet. En cas d'arrêt brutal, ils indiquent au script 
que le travail a déjà été effectué dans une sous-section. Ils servent aussi de rapport d'état : si 
une catégorie est inaccessible, le fichier inscrit la mention VIDE. Enfin, il enregistre le ratio 
entre les articles attendus et ceux réellement téléchargés pour faciliter la vérification finale. 

## Constitution de la base de données
Une fois les 3,8 Go de fichiers HTML stockés localement, nous avons développé un second 
script dédié à l’extraction des informations pour transformer le tout en une base de données 
exploitable. 

### Méthodologie d’extraction et de nettoyage 
Le défi de cette étape n'est pas seulement de lire du texte, mais de le rendre "analysable". Pour 
cela, nous avons suivi trois principes :

- L’utilisation des expressions régulières (Regex) : Nous avons utilisé Regex pour extraire 
les données tout en contrôlant leur format. Pour s’adapter aux variations du site, nous 
avons développé plusieurs expressions pour une seul variable. La variable 
"Dimensions" a été la plus complexe à traiter : elle apparaît soit sous forme de bloc (L 
x l x H), soit via des intitulés séparés (Longueur, Largeur...). De plus, nous avons dû 
gérer l'hétérogénéité des unités (mètres, centimètres ou millimètres) pour tout renvoyer 
en cm.
- La standardisation et la création de variables : Pour rendre les données exploitables, 
nous avons transformé certains textes en valeurs numériques. Par exemple, un prix 
stocké sous la forme "1 290,00 €" a été converti en nombre (1290.0). Nous avons 
également créé des variables binaires, comme la "Livraison gratuite" : le script compare 
automatiquement le prix du produit au seuil de gratuité de frais de port indiqué sur la 
page pour renvoyer "Oui" ou "Non". 
- La sécurité anti-crash : Sur 7 600 fichiers, certains présentent inévitablement des 
anomalies de saisie ou même des valeurs manquantes. Pour éviter que le script ne 
s'arrête, nous avons intégré des blocs try...except. En complément, nous avons 
systématiquement remplacé les virgules par des points dans les variables numériques 
pour garantir la conversion des textes en nombres sans erreur.

### Structure de la base finale 
La base de données finale regroupe 7 625 articles uniques. Chaque ligne représente un produit 
et chaque colonne une variable spécifique. 
Tableau des variables créées :  

<img width="760" height="356" alt="image" src="https://github.com/user-attachments/assets/233d98bf-ee3f-434e-9787-66891fa830d8" />

### Petite analyse de la base de données 
L’analyse de la base de données met en évidence une structure de marché équilibrée.  

<img width="458" height="247" alt="image" src="https://github.com/user-attachments/assets/fbc4060b-dcee-46d2-a12d-33335bd1d372" />

Le Graphique 1  montre qu’aucune marque ne monopolise le catalogue, avec Yamaha 
en tête (4,8 %) devant Thomann (4,3 %) et Doepfer (3,9 %).  

<img width="379" height="296" alt="image" src="https://github.com/user-attachments/assets/15160c00-2729-49d7-a64f-3d8bb3f6764a" />

Sur le plan logistique, le Graphique 2  témoigne d’une excellente réactivité : plus de 77 % des articles sont en stock 
immédiat. L’étude de la satisfaction client (Graphique 3) est très positive : sur les 
produits ayant reçu une évaluation, une écrasante majorité des clients se déclare "Très satisfaite" 
(48 %). Enfin, l’amplitude des prix illustre la diversité de l’offre, allant de 0,49 € pour un 
bouchon Jaspers à 70 490 € pour un piano Yamaha D C6 X.  

<img width="377" height="268" alt="image" src="https://github.com/user-attachments/assets/5314e5ef-e3e5-469b-a254-b26e0f4e9a4c" />

