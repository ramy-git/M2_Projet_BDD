# ETL pipeline

![Pipeline-Diagram]()

- [INDEX]()
  * [Tech Stack](#tech-stack)
  * [Description](#description)
  * [Pipeline](#pipeline)
    + [Tweet Collector](#tweet-collector)
    + [MongoDB](#mongodb)
    + [Postgres SQL](#postgres-sql)
    + [ETL Job](#etl-job)
    + [Discordbot](#Discordbot)
  * [Equipe](#equipe)
  * [Perspective](#perspective)

### Tech Stack
- Python 3.8 ( libraries dans requirements.txt)
- Twitter API
- MongoDB
- Postgres SQL
- Docker
- Discord (WebHook)


## Description
Un projet dans le cadre de l'UE base de donnée du Master 2 STDS , comprennant une pipeline ETL qui collecte des tweets en temps réel à partir de l'API Twitter mentionnant ou provenant de differents acteurs crypto sur Twitter. Il attribue un score de sentiment à ces tweets et publie le tweet ayant le meilleur et le pire score par heure sur un channel discord via un webhook.

## The Pipeline 

Le pipeline se compose de 5 éléments :

### Tweet Collector

Un script python qui utilise la bibliothèque Tweepy pour écouter les flux de l'API Twitter en temps réel. Si l'un des tweets écoutés mentionne l'un des leaders mondiaux choisis, il est capturé et prétraité (nous ne sommes intéressés que par le texte original du tweet et nous obtenons l'original à partir des retweets) et stocké dans MongoDB.

### MongoDB

MongoDB est notre DataLake , où nous envyons les tweets collectés par le Tweet Collector. l'ETL lit MongoDB (pour le traitement) au contraite de  Tweet Collector qui y écrit. 

### Postgres SQL

Le Postgres SQL est notre Data Warehouse. Nous y stockons les tweets analysés en termes de sentiment et horodatés. Le travail ETL écrit dans Postgres et DiscordBot lit à partir de celui-ci. 

### ETL Job

Un script python qui lit les tweets dans MongoDB, effectue une analyse des sentiments sur ceux-ci, puis les écrit dans Postgres avec leur timestamp.

### Discordbot

Un script python qui lit le tweet le plus positif et le plus negatitf dans la bdd Postgres toutes les heures et les publie sur le channel discord sélectionné.

Chaque composant s'exécute sur la machine locale dans son propre conteneur docker, ces conteneurs sont gérés par docker compose.

## Equipe
- M2 STDS FI 
- <a href="https://github.com/ramy-git">@ramy-git</a> Ramy T.
- Mustapha B.


### Perspective

-  seuls 100 tweets d'intérêt (tweets suivis) sont traités par période de 5 minutes. Lire plus de tweets est possible avec les identifiants gratuits de l'API Twitter, mais nous avons choisi de nous limiter à ce rythme.

- le timing des scripts est géré par des instructions sleep à l'intérieur des scripts. Il existe de meilleures technologies pour gérer la communication entre les différents composants et les orchestrer (Kubernetes, Apache Kafka, Apache Airflow ...). 

-  Une une gestion des erreurs adéquates doivent être mises en place. À ce stade, la gestion des erreurs n'est que très peu fonctionnelle.

- La webhook n'est pas encore totalement operationnelle pour Discord , elle marche bien pour d'autres services ( ex : slack)


