# Système de Contrôle Électoral Ultra-Résistant à la Fraude

UFRECS, également appelé ainsi, est un système de contrôle électoral conçu pour être ultra-résistant à la fraude.

Il est destiné à être utilisé contre les gouvernements délinquants qui n’hésitent pas à truquer les élections pour rester au pouvoir.

## 1. **Méthodes utilisées par les systèmes corrompus pour frauder aux élections**

### **A. Manipulation en amont du scrutin**

* **Falsification du registre électoral** : ajout de noms fictifs ou suppression de noms réels pour influencer le nombre de votants.
* **Distribution inégale des cartes d’électeurs** : cartes volontairement retenues ou remises aux partisans du régime en place.
* **Gerrymandering** (redécoupage électoral partisan) : modification des limites des circonscriptions pour favoriser un parti.

### **B. Manipulation pendant le vote**

* **Bourrage d’urnes** : ajout de bulletins supplémentaires par des agents électoraux corrompus.
* **Votes multiples** : une même personne votant plusieurs fois avec différentes identités.
* **Intimidation des électeurs** : présence de milices ou de forces armées aux bureaux de vote pour influencer le choix ou décourager certains votants.
* **Empêchement physique de voter** : fermeture anticipée des bureaux, retards dans l’ouverture, absence de matériel électoral dans certaines zones.
* **Vote par procuration abusif** : utilisation illégale du vote pour des personnes absentes ou décédées.

### **C. Manipulation lors du dépouillement et de la transmission**

* **Modification des procès-verbaux** : falsification des chiffres lors du transfert des résultats vers les instances centrales.
* **Logiciels truqués** : manipulation des systèmes électroniques de vote ou de comptage pour favoriser un candidat.
* **Résultats gonflés ou minimisés** : ajout ou suppression de votes lors du calcul final.
* **Blocage ou dissimulation des résultats locaux** : retard volontaire dans l’annonce de certaines zones pour préparer une version “officielle” falsifiée.

### **D. Stratégies d’influence indirecte**

* **Achat de votes** : distribution d’argent, cadeaux ou promesses en échange de votes.
* **Propagande disproportionnée** : accès exclusif aux médias d’État, diffamation des opposants.
* **Utilisation de l’appareil d’État** : ressources publiques mises au service d’un candidat.

---

## 2. **Mesures pratiques pour prévenir et contrôler les élections**

### **A. Avant l’élection**

1. **Contrôle citoyen du registre électoral**

   * Organisation de comités locaux pour vérifier que chaque citoyen est inscrit correctement.
   * Signalement public des anomalies (noms fictifs, disparus, doublons).
2. **Formation des observateurs**

   * Formation de volontaires sur les procédures officielles de vote et dépouillement.
   * Collaboration avec des ONG et observateurs internationaux.

### **B. Pendant le scrutin**

1. **Présence massive d’observateurs**

   * Observateurs indépendants dans chaque bureau de vote.
   * Vidéosurveillance ou enregistrement des opérations (si légalement possible).
2. **Transparence du processus**

   * Affichage public des listes d’électeurs à l’entrée.
   * Comptage des bulletins devant témoins.
3. **Signalement en temps réel**

   * Utilisation d’applications sécurisées pour rapporter des incidents (photos, vidéos, témoignages).

### **C. Après le vote**

1. **Vérification des procès-verbaux**

   * Chaque bureau affiche ses résultats localement avant transmission.
   * Comparaison des copies locales avec les résultats officiels annoncés.
2. **Centralisation citoyenne des données**

   * Plateformes collaboratives pour publier et comparer les résultats recueillis par les observateurs.
3. **Protection contre les manipulations informatiques**

   * Audit indépendant des logiciels de comptage et stockage sécurisé des données.

### **D. Pression publique et juridique**

* Mobilisation de la société civile pour exiger la publication intégrale et détaillée des résultats par bureau de vote.
* Actions en justice et dénonciations médiatiques en cas de fraude documentée.

## 3. **Quels points UFRECS résout-il ?**

UFRECS résout les méthodes utilisées pendant la journée électorale et après.

### **B. Le jour de l’élection**

1. **Présence massive d’observateurs indépendants**

Les citoyens ont confiance dans l’application de contrôle et sont certains de pouvoir l’utiliser sans enfreindre la loi.

2. **Transparence du processus**

Les rapporteurs peuvent rendre compte publiquement de leurs observations.  
L’application et le code source du backend sont open source et peuvent être vérifiés.  
Plusieurs personnes peuvent signaler pour le même bureau de vote, ce qui augmente la transparence.

3. **Signalement des incidents en temps réel**

L’application rapporte le dépouillement en temps réel. Le processus de vote peut également être diffusé en direct.  
Le comptage des votes se fait en temps réel, ce qui augmente la confiance des électeurs.

### **C. Après le vote**

Comme le comptage était en temps réel, à la fin du dépouillement les résultats sont déjà connus.  
Les différents rapports peuvent être comparés par bureau de vote en cas de divergences.  
Les personnes situées dans des zones sans réseau pour synchroniser le comptage en direct peuvent rapidement se déplacer vers une zone couverte par un réseau et laisser la synchronisation se faire.

Toutes ces vidéos, audios et rapports peuvent être présentés comme preuves en cas de présentation de résultats erronés.

## 4. **Comment ça fonctionne ?**


### A. Présentation générale du système UFRECS

Le système **UFRECS** (U-F-R-E-C-S) repose sur trois principales applications :

1. **Une application back-end**
2. **Une application mobile destinée aux rapporteurs**
3. **Une application mobile destinée aux citoyens**

Ces trois composantes interagissent pour permettre un suivi précis, en temps réel ou différé, des opérations de vote et de dépouillement dans chaque bureau de vote.

---

### B. Application Back-End

Le **back-end** est conçu pour supporter une charge extrêmement élevée, capable de gérer simultanément **plus de 100 millions d’utilisateurs connectés**.
Il s’appuie sur des technologies de **messagerie événementielle** (*event messaging*) afin de diffuser rapidement les mises à jour aux clients connectés.

Exemple de technologie utilisée : **RabbitMQ**, permettant d’envoyer des événements aux différentes applications clientes.

---

### C. Application Mobile du Rapporteur

L’application destinée aux **rapporteurs** est conçue pour être simple et intuitive. Elle offre deux modes principaux :

* **Mode "Vote en cours"**

  * Affichage d’un bouton **"Une personne vient d’entrer"** qui déclenche la prise d’une photo du citoyen entrant dans **l’isoloir**.
  * Ce bouton se transforme ensuite en deux options :

    * **"La personne est sortie"**
    * **"La personne est sortie et a déchiré"**
  * Des options supplémentaires permettent de renseigner le genre (homme/femme) et la tranche d’âge (jeune/adulte/vieux).
  * Une fois validée, l’information est envoyée au back-end pour mise à jour du nombre de votants.

* **Mode "Décompte des votes"**

  * Configuration préalable : choix de la source de vérité (audio ou vidéo).
  * En mode audio : enregistrement vocal du décompte.
  * En mode vidéo : enregistrement filmé du dépouillement.
  * L’interface présente les boutons correspondant à chaque **parti** et **candidat**. Chaque clic enregistre un vote, envoyé immédiatement ou stocké en attente si le réseau est indisponible.
  * Cette fonctionnalité permet un **décompte en temps réel** ou **différé mais exact**.
  * Plusieurs rapporteurs peuvent couvrir un même bureau, permettant une **vérification croisée des données**.

---

### D. Application Mobile du Citoyen

L’application citoyenne offre deux principales possibilités :

* **Suivi global** : consulter en temps réel l’évolution des votes au niveau national.
* **Suivi local** : choisir un bureau de vote spécifique et suivre ses mises à jour.

Elle permet aussi à un électeur de **vérifier que son vote a été pris en compte**. Lorsqu’il quitte le bureau, le rapporteur l’enregistre comme "sorti", ce qui déclenche l’envoi d’un événement au back-end, puis la mise à jour immédiate sur l’application citoyenne (avec statistiques de genre et d’âge).

---

### E. Fonctionnement global

1. Les rapporteurs enregistrent les entrées/sorties et le dépouillement via leur application.
2. Les données sont transmises au back-end, qui les diffuse aux citoyens et autres systèmes connectés.
3. Les citoyens peuvent vérifier en temps réel ou a posteriori l’évolution des résultats.
4. La conception du système garantit la **scalabilité**, la **résilience aux coupures réseau**, et la **transparence** dans le processus électoral.



## 5. **Feuille de route**

[] Décider comment cela fonctionnera
