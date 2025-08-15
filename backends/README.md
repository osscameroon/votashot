# UFRECS — Backend Overview

UFRECS is a web service exposing a REST API and a WebSocket channel to:

* authenticate **sources** (reporters);
* collect evidence (images/videos/audio) and voting events;
* publish **real-time statistics** per polling station;
* record and distribute **tallying results**;
* enable ephemeral **citizen verification** via WebSocket.

Media storage is on S3. Clients (mobile apps/bot) use **Basic Auth**: `username = elector_id`, `password = token` issued by the API.

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
````

### Behavior

* If `elector_id` exists: generate a **token** and associate it to the `poll_office_id`.
* If `elector_id` does not exist: create a **Source** with status `unknown/unverified`. This status may become `independent` after identity verification.
* Returns **S3 upload information** limited to the source’s scope:

  * `s3_base_path` (path dedicated to the source)
  * **temporary credentials/certificates** valid only for this path (principle of least privilege)

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

> Note: The **token** is tied to `poll_office_id`. The client no longer needs to repeat the polling station ID in subsequent calls.

---

## 2) S3 organization (media)

Within `s3.base_path`, the client creates standardized subfolders:

* `list-votes/`: photos of the polling station’s **posted lists** (named “1.jpeg”, “2.jpeg”, …).
* `counting-proof/`: continuous **audio/video** of the **tallying**.
* `verbal_process/`: images/videos of the final **official report (procès-verbal)**.
* `votes/`: shots related to a particular vote, named:
  `vote-{global_id}-{index}-{timestamp}.jpeg`
  (e.g., proof of entering the booth, a hand holding a torn ballot, etc., always without direct facial identification).

This convention makes persisting media links in the database unnecessary.

---

## 3) Election-day tracking (real-time stream)

### a) Recording a visit to the voting booth

The reporter marks the entry to and exit from the booth, then sends a **voting event**.

### Endpoint

`POST /api/vote/`

### Input (JSON)

```json
{
  "index": 1,                  // nth vote in the polling station (client counts 1,2,3…)
  "gender": "male|female",
  "age": "less_30|less_60|more_60",
  "has_torn": true|false
}
```

### Output (JSON)

```json
{
  "id": "15446546546",
  "index": 1
}
```

The client uses these identifiers to name and upload the media linked to the vote.

> Business goal: capture the pace of voting, distributions by sex/age group, and an indicator “ruling-party ballot torn” when spontaneously presented by the voter.

---

## 4) Real-time polling-station statistics

### Endpoint

`GET /api/pollofficesstats/{poll_office_id}/`

### Output (JSON)

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

> Requirement: **highly optimized** endpoint (the most requested of the day) for responsive dashboards and live animations.

---

## 5) Tallying (after polls close)

### a) Recording each tallied ballot

`POST /api/votingpaperresult/`

**Input**

```json
{ "index": 1, "party_id": "string" }
```

**Output**

```json
{ "status": "ok" }
```

### b) Public results for the polling station

`GET /api/pollofficeresults/{poll_office_id}/`

**Output**

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

In parallel, clients upload the **tallying audio/video** to `counting-proof/`, then images of the **official report** to `verbal_process/`.

---

## 6) Citizen verification (WebSocket)

### Channel

`WS /ws/vote-verification`

### Principle

1. The voter opens the WebSocket from the app upon entering the booth (“I am voting”).
2. As soon as a reporter posts the corresponding vote, the app **receives** via WS the declared attributes (gender, age group, “torn ballot” flag).
3. The voter **confirms or corrects** these attributes in the app.
4. The backend records the confirmation in the **`VoteVerified`** table (linked to the voter and the vote) to **strengthen credibility** of the observations.
5. The backend **closes the WS** and the app returns to the standard flow.

> Reliability relies on the **plurality of reporters** and the **match** between their reports and citizen confirmations.

---

## 7) “Source” model & states

* **Source = reporter** (or “opportunistic source” when no official reporter is present).
* On first unknown authentication: state `unknown/unverified` (allows not blocking upfront while filtering later).
* After identity verification: state `independent`.
  These statuses guide how the data is used/published.

---

## 8) Requirements for a “valid” backend

A UFRECS backend may be implemented in any technology **provided** it respects the API contract above and provides:

* **Documentation**: a `docs/` or `documentation/` folder.
* **Developer scripts**:

  * `setup-dev-mode.sh`: installs **all** dependencies and prepares the local environment.
  * `run-dev-mode`: starts the server in dev mode.
* **Deployment script**:

  * `install-home-prod`: end-to-end production provisioning (dependencies, server config, Nginx, etc.).
* **Tests**:

  * `run-test`: runs the full backend test suite.

Goals: **documented**, **tested**, **quick to install**, **swappable** (you can replace the backend as long as the API is respected).

---

## 9) Endpoint summary

| Use case                                  | Method & path                                  | Body/Parameters                             | Response                                   |
| ----------------------------------------- | ---------------------------------------------- | ------------------------------------------- | ------------------------------------------ |
| Authenticate a source & provide S3 access | `POST /api/authenticate/`                      | `elector_id`, `password?`, `poll_office_id` | `token`, `s3.base_path`, `s3.credentials`  |
| Record a vote (election day)              | `POST /api/vote/`                              | `index`, `gender`, `age`, `has_torn`        | `id`, `index`                              |
| Real-time station stats                   | `GET /api/pollofficesstats/{poll_office_id}/`  | —                                           | `totals`, `last_vote`                      |
| Record a tallied ballot                   | `POST /api/votingpaperresult/`                 | `index`, `party_id`                         | `{ "status": "ok" }`                       |
| Cumulative results for a station          | `GET /api/pollofficeresults/{poll_office_id}/` | —                                           | `last_paper`, `results[]`, `total_ballots` |
| Citizen verification                      | `WS /ws/vote-verification`                     | open WS on the citizen side                 | confirmations → record `VoteVerified`      |

---

## 10) Best practices & safeguards

* **Privacy**: shoot **from behind** and frame hands/object; prohibit facial identification.
* **Security**: short/rotating tokens; S3 access **path-scoped**; audit logs.
* **Resilience**: **idempotent** clients (safe re-submission), queues/retry on backend along critical paths.
* **Performance**: `GET /api/pollofficesstats/` must be **very fast** (cache/aggregates).

---

## 11) Diagram

```mermaid
%% GitHub-compatible Mermaid sequence diagram of UFRECS interactions
sequenceDiagram
    autonumber

    participant Reporter as Reporter App (Source)
    participant API as UFRECS REST API
    participant WS as UFRECS WebSocket
    participant S3 as S3 Storage
    participant Dash as Dashboard/Observer
    participant Voter as Voter App (Citizen)
    participant Public as Public Client

    %% 1) Authentication & S3 provisioning
    Note over Reporter,API: 1) Authentication & S3 provisioning
    Reporter->>API: POST /api/authenticate {elector_id, password?, poll_office_id}
    alt elector_id exists
        API->>API: Generate token & bind to poll_office_id
    else new elector_id
        API->>API: Create Source with status "unknown/unverified"
    end
    API-->>Reporter: 200 {token, poll_office_id, s3.base_path, s3.credentials}
    Note right of Reporter: Subsequent Basic Auth\nusername = elector_id\npassword = token

    %% 2) Media organization (naming happens client-side)
    Note over Reporter,S3: Client uploads under s3.base_path/\nlist-votes/, votes/, counting-proof/, verbal_process/\n(no facial identification; frame hands/objects)

    %% 3) Election-day tracking (real-time)
    Note over Reporter,API: 3) Election-day tracking
    loop For each voter
        Reporter->>API: POST /api/vote {index, gender, age, has_torn}
        API-->>Reporter: 200 {id, index}
        Reporter->>S3: Upload vote media\nvotes/vote-{global_id}-{index}-{ts}.jpeg
        Dash->>API: GET /api/pollofficesstats/{poll_office_id}
        API-->>Dash: {totals, last_vote}
    end

    %% 6) Citizen verification (WebSocket)
    Note over Voter,WS: 6) Citizen verification via WS
    Voter->>WS: OPEN WS /ws/vote-verification ("I'm voting")
    API-->>WS: On matching vote: send {gender, age, has_torn}
    WS-->>Voter: Receive attributes
    Voter->>WS: Confirm/correct attributes
    WS->>API: Save VoteVerified (linked voter↔vote)
    API-->>WS: Close channel

    %% 5) Tallying after polls close
    Note over Reporter,API: 5) Tallying after close
    loop For each paper ballot counted
        Reporter->>API: POST /api/votingpaperresult {index, party_id}
        API-->>Reporter: {status: "ok"}
    end
    Reporter->>S3: Upload counting-proof/ (A/V)\nthen verbal_process/ (official report images)
    Public->>API: GET /api/pollofficeresults/{poll_office_id}
    API-->>Public: {last_paper, results[], total_ballots}

    %% 10) Safeguards (non-functional)
    Note over API,S3: Security: short/rotating tokens; S3 creds scoped to base_path; audit logs
    Note over API,Dash: Performance: /api/pollofficesstats/ must be very fast (cache/aggregates)
```
