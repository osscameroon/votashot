# UFRECS — Backend Overview 

UFRECS is a web service exposing a REST API and a WebSocket channel to:

* authenticate **sources** (reporters);
* collect evidence (images/videos/audio) and voting events;
* publish **real-time statistics** per polling station;
* record and distribute **tallying results**;
* enable ephemeral **citizen verification** via WebSocket.

Media storage is on S3. Clients (mobile apps/bots) use **Basic Auth**: `username = elector_id`, `password = token` issued by the API.

> Note: The token is **linked to a poll\_office\_id** to scope write operations and S3 access. It does **not** auto-fill the `poll_office` query parameter on the modified GET endpoints below.

---

## 1) Authentication & S3 provisioning

### Endpoint

`POST /api/authenticate/`

### Input (JSON)

```json
{
  "elector_id": "string (required, unique)",
  "password": "string (optional)",
  "poll_office_id": "string (required)"
}
```

### Behavior

* If `elector_id` exists: generate a **token** and bind it to `poll_office_id`.
* If `elector_id` does not exist: create a **Source** with status `unknown/unverified` (may become `independent` after KYC).
* Return **S3 upload info** limited to the source’s scope:

  * `s3_base_path` (path dedicated to the source)
  * **temporary credentials** valid only for this path (least-privilege)

### Output (JSON)

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

## 2) S3 organization (media)

Within `s3.base_path`, clients create standardized subfolders:

* `list-votes/`: photos of the station’s **posted lists** (named `1.jpeg`, `2.jpeg`, …).
* `counting-proof/`: continuous **audio/video** of the **tallying**.
* `verbal_process/`: images/videos of the final **official report (procès-verbal)**.
* `votes/`: media tied to a particular vote, named
  `vote-{global_id}-{index}-{timestamp}.jpeg`
  (e.g., booth entry proof, hand holding a torn ballot; **no direct facial ID**).

This convention makes persisting media URLs in the database unnecessary.

---

## 3) Election-day tracking (real-time)

### Record a visit to the voting booth

The reporter marks booth entry/exit, then sends a **voting event**.

**Endpoint**
`POST /api/vote/`

**Input (JSON)**

```json
{
  "index": 1,                  // nth vote at the station (client counts 1,2,3…)
  "gender": "male|female",
  "age": "less_30|less_60|more_60",
  "has_torn": true
}
```

**Output (JSON)**

```json
{ "id": "15446546546", "index": 1 }
```

Clients use these identifiers to name and upload the related vote media.

> Business goal: capture vote cadence, sex/age distributions, and a “ruling-party ballot torn” indicator when shown spontaneously by the voter.

---

## 4) Polling offices directory (**new**)

**Endpoint**
`GET /api/polloffices/`

**Output (JSON)**

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

## 5) Real-time polling-station statistics (**modified**)

**Endpoint**
`GET /api/pollofficesstats/?poll_office={poll_office_id}`

* **When `poll_office` is provided (single ID):** returns the **same schema** as before for that station.
* **When `poll_office` is omitted:** returns stats **for all polling stations**.

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

> Performance requirement: this endpoint must be **very fast** (cache/aggregates), as it is heavily polled by dashboards/live animations.

---

## 6) Tallying (after polls close)

### a) Record each tallied ballot

`POST /api/votingpaperresult/`

**Input**

```json
{ "index": 1, "party_id": "string" }
```

**Output**

```json
{ "status": "ok" }
```

### b) Public results (**modified retrieval URL**)

`GET /api/pollofficeresults/?poll_office={poll_office_id}`

* **When `poll_office` is provided (single ID):** returns the **same schema** as before for that station.
* **When `poll_office` is omitted:** returns results **for all polling stations**.

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

In parallel, clients upload **tallying A/V** to `counting-proof/` and **official report** images to `verbal_process/`.

---

## 7) Citizen verification (WebSocket)

**Channel**
`WS /ws/vote-verification`

**Flow**

1. Voter opens the WebSocket upon entering the booth (“I am voting”).
2. When a reporter posts the corresponding vote, the app **receives** the declared attributes (gender, age group, `has_torn`).
3. The voter **confirms or corrects** these attributes.
4. Backend records the confirmation in **`VoteVerified`** (links voter ↔ vote) to **strengthen credibility**.
5. Backend **closes** the WS; the app returns to the standard flow.

Reliability depends on **plurality of reporters** and **concordance** with citizen confirmations.

---

## 8) “Source” model & states

* **Source = reporter** (or “opportunistic source” when no official reporter is present).
* On first unknown authentication: state `unknown/unverified` (allows participation while enabling downstream filtering).
* After identity verification: state `independent`.
  These statuses guide data usage/publication.

---

## 9) Create reporter/source (**new**)

**Endpoint**
`POST /api/reporters/`

**Body**

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

## 10) Requirements for a “valid” backend

A UFRECS backend may be implemented in any technology **provided** it respects the API contract and includes:

* **Documentation**: `docs/` or `documentation/`.
* **Developer scripts**:

  * `setup-dev-mode.sh`: install **all** dependencies and prep local env.
  * `run-dev-mode.sh`: start the server in dev mode.
* **Deployment script**:

  * `install-home-prod.sh`: end-to-end production provisioning (deps, server config, Nginx, etc.).
* **Tests**:

  * `run-tests.sh`: run the complete backend test suite.

Goals: **documented**, **tested**, **quick to install**, **swappable** (backend can be replaced as long as the API is honored).

---

## 11) Endpoint summary (updated)

| Use case                     | Method & path                                  | Params/Body                                                                | Response                                       |
| ---------------------------- | ---------------------------------------------- | -------------------------------------------------------------------------- | ---------------------------------------------- |
| List polling stations        | `GET /api/polloffices/`                        | —                                                                          | `poll_offices[]` with attributes               |
| Create reporter/source       | `POST /api/reporters/`                         | `elector_id`, `type`, `official_org`, `full_name`, `email`, `phone_number` | `{status:"created", source{...}}`              |
| Authenticate & S3 access     | `POST /api/authenticate/`                      | `elector_id`, `password?`, `poll_office_id`                                | `token`, `s3.base_path`, `s3.credentials`      |
| Record a vote (election day) | `POST /api/vote/`                              | `index`, `gender`, `age`, `has_torn`                                       | `{id, index}`                                  |
| Real-time stats (one/all)    | `GET /api/pollofficesstats/?poll_office={id}`  | query optional                                                             | single-station object **or** `{offices:[...]}` |
| Record tallied ballot        | `POST /api/votingpaperresult/`                 | `index`, `party_id`                                                        | `{status:"ok"}`                                |
| Results (one/all)            | `GET /api/pollofficeresults/?poll_office={id}` | query optional                                                             | single-station object **or** `{offices:[...]}` |

---

## 12) Best practices & safeguards

* **Privacy**: shoot **from behind**; frame hands/objects; avoid facial identification.
* **Security**: short/rotating tokens; path-scoped S3 creds; audit logs.
* **Resilience**: **idempotent** clients (safe re-submit); backend queues/retries on critical paths.
* **Performance**: `/api/pollofficesstats/` must be **very fast** (cache/aggregates).

---

## 13) Diagram

```mermaid
%% UFRECS interactions with updated endpoints (GitHub-compatible)
sequenceDiagram
    autonumber

    participant Admin as Admin/Org Operator
    participant Reporter as Reporter App (Source)
    participant API as UFRECS REST API
    participant WS as UFRECS WebSocket
    participant S3 as S3 Storage
    participant Dash as Dashboard/Observer
    participant Voter as Voter App (Citizen)
    participant Public as Public Client

    %% 0) Onboarding: create reporter/source (NEW)
    Admin->>API: POST /api/reporters {elector_id, type, official_org, full_name, email, phone_number}
    API-->>Admin: 201 {status:"created", source:{id, elector_id, state:"unknown/unverified"}}

    %% 1) Authentication & S3 provisioning
    Reporter->>API: POST /api/authenticate {elector_id, password?, poll_office_id}
    API->>API: Create/lookup Source; issue token bound to poll_office_id
    API-->>Reporter: 200 {token, poll_office_id, s3.base_path, s3.credentials}
    Note right of Reporter: Basic Auth thereafter:\nusername=elector_id, password=token

    %% 2) Media uploads layout
    Note over Reporter,S3: Client uploads under s3.base_path/\n- list-votes/\n- votes/\n- counting-proof/\n- verbal_process/\n(No facial identification)

    %% 3) Election-day tracking
    loop For each voter
        Reporter->>API: POST /api/vote {index, gender, age, has_torn}
        API-->>Reporter: 200 {id, index}
        Reporter->>S3: Upload votes/vote-{global_id}-{index}-{ts}.jpeg
    end

    %% 4) Polling-station directory (NEW)
    Public->>API: GET /api/polloffices/
    API-->>Public: 200 {poll_offices:[{identifier, name, country, state, region, city, county, district}, ...]}

    %% 5) Real-time stats (MODIFIED URL)
    Dash->>API: GET /api/pollofficesstats/?poll_office=PO-001
    API-->>Dash: 200 {totals, last_vote}
    Dash->>API: GET /api/pollofficesstats/  %% no query → all stations
    API-->>Dash: 200 {offices:[{poll_office_id, totals, last_vote}, ...]}
    Note over API,Dash: Must be highly optimized (cache/aggregates)

    %% 6) Citizen verification via WebSocket
    Voter->>WS: OPEN /ws/vote-verification ("I'm voting")
    WS-->>Voter: Attributes {gender, age, has_torn}
    Voter->>WS: Confirm/correct
    WS->>API: Save VoteVerified (link voter↔vote)
    API-->>WS: Close channel

    %% 7) Tallying & public results (MODIFIED URL)
    loop For each counted paper ballot
        Reporter->>API: POST /api/votingpaperresult {index, party_id}
        API-->>Reporter: 200 {status:"ok"}
    end
    Reporter->>S3: Upload counting-proof/ (A/V) and verbal_process/ (images)
    Public->>API: GET /api/pollofficeresults/?poll_office=PO-001
    API-->>Public: 200 {last_paper, results[], total_ballots}
    Public->>API: GET /api/pollofficeresults/  %% no query → all stations
    API-->>Public: 200 {offices:[{poll_office_id, last_paper, results[], total_ballots}, ...]}

    %% Non-functional safeguards
    Note over API,S3: Security: short/rotating tokens; path-scoped S3 creds; audit logs
```
