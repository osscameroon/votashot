# UFRECS — Vue d'ensemble du backend

UFRECS est un service web exposant une API REST et un canal WebSocket pour :

* authentifier des **sources** (reporters) ;
* collecter des preuves (images/vidéos/audio) et des événements de vote ;
* publier des **statistiques en temps réel** par bureau de vote ;
* enregistrer et diffuser les **résultats du dépouillement** ;
* permettre une **vérification citoyenne** éphémère via WebSocket.

Le stockage des médias se fait sur S3. Les clients (applications mobiles/bots) utilisent **Basic Auth** : `username = elector_id`, `password = token` émis par l’API.

> Remarque : Le jeton est **lié à un `poll_office_id`** afin de borner les opérations d’écriture et l’accès S3. Il **ne** préremplit **pas** le paramètre de requête `poll_office` sur les endpoints GET modifiés ci-dessous.

---

## 1) Authentification & provisionnement S3

### Endpoint

`POST /api/authenticate/`

### Entrée (JSON)

```json
{
  "elector_id": "chaîne (requis, unique)",
  "password": "chaîne (facultatif)",
  "poll_office_id": "chaîne (requis)"
}
```

### Comportement

* Si `elector_id` existe : générer un **token** et le lier à `poll_office_id`.
* Si `elector_id` n’existe pas : créer une **Source** avec l’état `unknown/unverified` (pouvant devenir `independent` après KYC).
* Retourner les **informations d’upload S3** limitées au périmètre de la source :

  * `s3_base_path` (chemin dédié à la source)
  * **identifiants temporaires** valables uniquement pour ce chemin (moindre privilège)

### Sortie (JSON)

```json
{
  "token": "string",
  "poll_office_id": "string",
  "s3": {
    "base_path": "s3://bucket/.../source-{elector_id}/",
    "credentials": { "access_key": "...", "secret_key": "...", "session_token": "..." }
  }
}
```

---

## 2) Organisation S3 (médias)

À l’intérieur de `s3.base_path`, les clients créent des sous-dossiers standardisés :

* `list-votes/` : photos des **listes affichées** du bureau (nommées `1.jpeg`, `2.jpeg`, …).
* `counting-proof/` : **audio/vidéo** continu(e) du **dépouillement**.
* `verbal_process/` : images/vidéos du **rapport officiel final (procès-verbal)**.
* `votes/` : médias liés à un vote particulier, nommés
  `vote-{global_id}-{index}-{timestamp}.jpeg`
  (p. ex. preuve d’entrée dans l’isoloir, main tenant un bulletin déchiré ; **pas d’identification faciale directe**).

Cette convention rend inutile la persistance des URL des médias dans la base de données.

---

## 3) Suivi le jour du scrutin (temps réel)

### Enregistrer une visite à l’isoloir

Le reporter marque l’entrée/sortie de l’isoloir, puis envoie un **événement de vote**.

**Endpoint**
`POST /api/vote/`

**Entrée (JSON)**

```json
{
  "index": 1,                  // nᵉ vote au bureau (le client compte 1,2,3…)
  "gender": "male|female",
  "age": "less_30|less_60|more_60",
  "has_torn": true
}
```

**Sortie (JSON)**

```json
{ "id": "15446546546", "index": 1 }
```

Les clients utilisent ces identifiants pour nommer et téléverser les médias liés au vote.

> Objectif métier : capturer la cadence de vote, les distributions par sexe/âge, et un indicateur « bulletin du parti au pouvoir déchiré » lorsqu’il est montré spontanément par l’électeur.

---

## 4) Répertoire des bureaux de vote (**nouveau**)

**Endpoint**
`GET /api/polloffices/`

**Sortie (JSON)**

```json
{
  "total": 40000,
  "next": "",
  "previous": "",
  "results": [
    {
      "name": "Lycée Municipal A",
      "identifier": "PO-001",
      "country": "CM",
      "state": "Littoral",
      "region": "Littoral",
      "city": "Douala",
      "county": "Wouri",
      "district": "Akwa"
    }
  ]
}
```

---

## 5) Statistiques des bureaux de vote en temps réel (**modifié**)

**Endpoint**
`GET /api/pollofficesstats/?poll_office={poll_office_id}`

* **Quand `poll_office` est fourni (ID unique)** : renvoie le **même schéma** qu’auparavant pour ce bureau.
* **Quand `poll_office` est omis** : renvoie des stats **pour tous les bureaux de vote**.

```json
{
  "totals": {
    "votes": 123,
    "male": 60,
    "female": 62,
    "less_30": 40,
    "less_60": 60,
    "more_60": 18,
    "has_torn": 7
  },
  "last_vote": {
    "index": 123,
    "gender": "female",
    "age": "less_60",
    "has_torn": false,
    "timestamp": "2025-08-15T14:02:11Z"
  }
}
```

> Exigence de performance : cet endpoint doit être **très rapide** (cache/agrégats), car il est fortement sollicité par les tableaux de bord/animations en direct.

---

## 6) Dépouillement (après la fermeture des bureaux)

### a) Enregistrer chaque bulletin dépouillé

`POST /api/votingpaperresult/`

**Entrée**

```json
{ "index": 1, "party_id": "string" }
```

**Sortie**

```json
{ "status": "ok" }
```

### b) Résultats publics (**URL de récupération modifiée**)

`GET /api/pollofficeresults/?poll_office={poll_office_id}`

* **Quand `poll_office` est fourni (ID unique)** : renvoie le **même schéma** qu’auparavant pour ce bureau.
* **Quand `poll_office` est omis** : renvoie les résultats **pour tous les bureaux de vote**.

```json
{
  "last_paper": { "index": 250, "party_id": "ABC" },
  "results": [
    { "party_id": "ABC", "ballots": 120, "share": 0.48 },
    { "party_id": "DEF", "ballots": 100, "share": 0.40 },
    { "party_id": "GHI", "ballots": 30,  "share": 0.12 }
  ],
  "total_ballots": 250
}
```

En parallèle, les clients téléversent l’**A/V du dépouillement** dans `counting-proof/` et les images du **procès-verbal** dans `verbal_process/`.

---

## 7) Vérification citoyenne (WebSocket)

**Canal**
`WS /ws/vote-verification`

**Flux**

1. L’électeur ouvre le WebSocket en entrant dans l’isoloir (« Je vote »).
2. Lorsqu’un reporter publie le vote correspondant, l’application **reçoit** les attributs déclarés (sexe, tranche d’âge, `has_torn`).
3. L’électeur **confirme ou corrige** ces attributs.
4. Le backend enregistre la confirmation dans **`VoteVerified`** (lien électeur ↔ vote) pour **renforcer la crédibilité**.
5. Le backend **ferme** le WS ; l’application revient au flux standard.

La fiabilité dépend de la **pluralité des reporters** et de la **concordance** avec les confirmations citoyennes.

---

## 8) Modèle « Source » & états

* **Source = reporter** (ou « source opportuniste » lorsqu’aucun reporter officiel n’est présent).
* À la première authentification inconnue : état `unknown/unverified` (autorise la participation tout en permettant un filtrage en aval).
* Après vérification d’identité : état `independent`.
  Ces statuts guident l’usage et la publication des données.

---

## 9) Créer un reporter/source (**nouveau**)

**Endpoint**
`POST /api/reporters/`

**Corps**

```json
{
  "elector_id": "string",
  "type": "string",
  "official_org": "string",
  "full_name": "string",
  "email": "string",
  "phone_number": "string"
}
```

---

## 10) Exigences pour un backend « valide »

Un backend UFRECS peut être implémenté dans n’importe quelle technologie **à condition** de respecter le contrat d’API et d’inclure :

* **Documentation** : `docs/` ou `documentation/`.
* **Scripts développeur** :

  * `setup-dev-mode.sh` : installer **toutes** les dépendances et préparer l’environnement local.
  * `run-dev-mode.sh` : démarrer le serveur en mode développement.
* **Script de déploiement** :

  * `install-home-prod.sh` : provisioning de production de bout en bout (dépendances, configuration serveur, Nginx, etc.).
* **Tests** :

  * `run-tests.sh` : exécuter l’ensemble de la suite de tests backend.

Objectifs : **documenté**, **testé**, **rapide à installer**, **interchangeable** (le backend peut être remplacé tant que l’API est respectée).

---

## 11) Récapitulatif des endpoints (mis à jour)

| Cas d’usage                  | Méthode & chemin                               | Paramètres/Corps                                                           | Réponse                                         |
| ---------------------------- | ---------------------------------------------- | -------------------------------------------------------------------------- | ----------------------------------------------- |
| Lister les bureaux de vote   | `GET /api/polloffices/`                        | —                                                                          | `poll_offices[]` avec attributs                 |
| Créer reporter/source        | `POST /api/reporters/`                         | `elector_id`, `type`, `official_org`, `full_name`, `email`, `phone_number` | `{status:"created", source{...}}`               |
| Authentifier & accès S3      | `POST /api/authenticate/`                      | `elector_id`, `password?`, `poll_office_id`                                | `token`, `s3.base_path`, `s3.credentials`       |
| Enregistrer un vote (jour J) | `POST /api/vote/`                              | `index`, `gender`, `age`, `has_torn`                                       | `{id, index}`                                   |
| Stats temps réel (un/tous)   | `GET /api/pollofficesstats/?poll_office={id}`  | requête facultative                                                        | objet d’un seul bureau **ou** `{offices:[...]}` |
| Enregistrer bulletin compté  | `POST /api/votingpaperresult/`                 | `index`, `party_id`                                                        | `{status:"ok"}`                                 |
| Résultats (un/tous)          | `GET /api/pollofficeresults/?poll_office={id}` | requête facultative                                                        | objet d’un seul bureau **ou** `{offices:[...]}` |

---

## 12) Bonnes pratiques & garde-fous

* **Vie privée** : filmer **depuis l’arrière** ; cadrer mains/objets ; éviter l’identification faciale.
* **Sécurité** : jetons courts/rotatifs ; identifiants S3 limités au chemin ; journaux d’audit.
* **Résilience** : clients **idempotents** (ré-envoi sûr) ; files d’attente/retry côté backend sur les chemins critiques.
* **Performance** : `/api/pollofficesstats/` doit être **très rapide** (cache/agrégats).

---

## 13) Schéma

```mermaid
%% Interactions UFRECS avec endpoints mis à jour (compatible GitHub)
sequenceDiagram
    autonumber

    participant Admin as Admin/Opérateur d'organisation
    participant Reporter as Application Reporter (Source)
    participant API as API REST UFRECS
    participant WS as WebSocket UFRECS
    participant S3 as Stockage S3
    participant Dash as Tableau de bord/Observateur
    participant Voter as Application Électeur (Citoyen)
    participant Public as Client Public

    %% 0) Onboarding : créer un reporter/source (NOUVEAU)
    Admin->>API: POST /api/reporters {elector_id, type, official_org, full_name, email, phone_number}
    API-->>Admin: 201 {status:"created", source:{id, elector_id, state:"unknown/unverified"}}

    %% 1) Authentification & provisionnement S3
    Reporter->>API: POST /api/authenticate {elector_id, password?, poll_office_id}
    API->>API: Créer/retrouver Source ; émettre un token lié à poll_office_id
    API-->>Reporter: 200 {token, poll_office_id, s3.base_path, s3.credentials}
    Note right of Reporter: Basic Auth ensuite :\nusername=elector_id, password=token

    %% 2) Organisation des uploads média
    Note over Reporter,S3: Le client téléverse sous s3.base_path/\n- list-votes/\n- votes/\n- counting-proof/\n- verbal_process/\n(Pas d’identification faciale)

    %% 3) Suivi du jour J
    loop Pour chaque électeur
        Reporter->>API: POST /api/vote {index, gender, age, has_torn}
        API-->>Reporter: 200 {id, index}
        Reporter->>S3: Upload votes/vote-{global_id}-{index}-{ts}.jpeg
    end

    %% 4) Répertoire des bureaux (NOUVEAU)
    Public->>API: GET /api/polloffices/
    API-->>Public: 200 {poll_offices:[{identifier, name, country, state, region, city, county, district}, ...]}

    %% 5) Stats temps réel (URL MODIFIÉE)
    Dash->>API: GET /api/pollofficesstats/?poll_office=PO-001
    API-->>Dash: 200 {totals, last_vote}
    Dash->>API: GET /api/pollofficesstats/  %% pas de requête → tous les bureaux
    API-->>Dash: 200 {offices:[{poll_office_id, totals, last_vote}, ...]}
    Note over API,Dash: Doit être très optimisé (cache/agrégats)

    %% 6) Vérification citoyenne via WebSocket
    Voter->>WS: OPEN /ws/vote-verification ("Je vote")
    WS-->>Voter: Attributs {gender, age, has_torn}
    Voter->>WS: Confirmer/corriger
    WS->>API: Enregistrer VoteVerified (lien électeur↔vote)
    API-->>WS: Fermer le canal

    %% 7) Dépouillement & résultats publics (URL MODIFIÉE)
    loop Pour chaque bulletin papier compté
        Reporter->>API: POST /api/votingpaperresult {index, party_id}
        API-->>Reporter: 200 {status:"ok"}
    end
    Reporter->>S3: Upload counting-proof/ (A/V) et verbal_process/ (images)
    Public->>API: GET /api/pollofficeresults/?poll_office=PO-001
    API-->>Public: 200 {last_paper, results[], total_ballots}
    Public->>API: GET /api/pollofficeresults/  %% pas de requête → tous les bureaux
    API-->>Public: 200 {offices:[{poll_office_id, last_paper, results[], total_ballots}, ...]}

    %% Garde-fous non fonctionnels
    Note over API,S3: Sécurité : jetons courts/rotatifs ; identifiants S3 limités au chemin ; journaux d’audit
```
