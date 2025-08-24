# Client Citoyen UFRECS

Un client citoyen UFRECS est toute application qui se connecte à un backend UFRECS afin de fournir
des données en temps réel (statistiques et résultats).

Le client propose 3 modes : Mode Statistiques, Mode Résultats et Mode Je-Vote.

## 1. Modes

### Mode Statistiques

Le mode Statistiques est un mode dans lequel le client affiche les statistiques concernant l’élection en cours.  
Les statistiques peuvent être affichées globalement ou par bureau de vote. L’utilisateur doit avoir
la possibilité de basculer d’une vue globale à une vue par bureau de vote.

Dans ce mode, l’application utilise l’endpoint `GET /api/pollofficesstats/?poll_office={poll_office_id}`
pour obtenir les statistiques.


### Mode Résultats

Le mode Résultats est un mode dans lequel le client affiche les résultats de l’élection en cours.  
Les résultats peuvent être affichés globalement ou par bureau de vote. L’utilisateur doit avoir
la possibilité de basculer d’une vue globale à une vue par bureau de vote.  
Les résultats correspondent ici au décompte des votes papier.

Dans ce mode, l’application utilise l’endpoint `GET /api/pollofficeresults/?poll_office={poll_office_id}`
pour obtenir les résultats.

### Mode Je-Vote

Le mode Je-Vote est un mode dans lequel l'utilisateur indique qu’il est en train de voter.  
Le client doit établir une connexion websocket à `WS /ws/vote-verification`. Ecouter le rapport du vote,  
que les rapporteurs/sources du bureau de vote feront. Ensuite, il confirme que les informations proposées  
sont correctes, puis revient en mode Statistiques.

## 2. Implémentations

Vous pouvez utiliser les technologies de votre choix. L’application peut prendre n’importe quelle forme :  
application mobile, bot ou site web.

## 3. Directives

L’application doit être très accessible. Toute personne avec des connaissances de base doit pouvoir l’utiliser.  
La règle des 3 clics doit être respectée. L’interface utilisateur doit être explicite par elle-même.
