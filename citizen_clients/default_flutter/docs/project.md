# Overview

This is an app which is called Ufrecs Citizen app

The app connects to UFRECS backend

# Pages

## Home page

image file : ./Home Page.jpg

Description: A page which 4 cards each cards bring to another page

Global Stats card: When clicked it brings to the Global Stats page

Global Results card: When clicked it brings to the Global Results page

Poll Office Stats card: When clicked it brings to the Select Poll Office Stats page

Poll Office Results card: When clicked it brings to the Select Poll Office Results page

## Select Poll Office Stats page

image file : ./Select Poll Office Stats.jpg

Description: A page which has a list of poll offices and a button "View Stats" to go to the Poll Office Stats page

## Select Poll Office Results page

image file : ./Select Poll Office Results.jpg

Description: A page which has a list of poll offices and a button "View Results" to go to the Poll Office Results page

## Global Stats page

image file : ./Global Stats.jpg

Description: A page which shows the stats of the election in all poll offices. There
is a table "Last Vote" which shows the specific stats of the last vote. Refresh stats
every 1 minute with beautiful animation to show stats changes.

Endpoint

`GET /api/pollofficesstats/`

* **When `poll_office` is provided (single ID):** returns the **same schema** as before for that station.
* **When `poll_office` is omitted:** returns stats **for all polling stations**.

```json
{
  "totals": {
    "total_poll_offices": 13344,
    "covered_poll_offices": 1000,
    "votes": 123,
    "male": 60,
    "female": 62,
    "less_30": 40,
    "less_60": 60,
    "more_60": 18,
    "has_torn": 7
  },
  "last_vote": {
    "Source 1": {
      "index": 123,
      "gender": "female",
      "age": "less_60",
      "has_torn": false,
      "timestamp": "2025-08-15T14:02:11Z"
    },
    "Source 2": {
      "index": 123,
      "gender": "female",
      "age": "less_60",
      "has_torn": false,
      "timestamp": "2025-08-15T14:02:11Z"
    },
    "Source ...": {
      "index": 123,
      "gender": "female",
      "age": "less_60",
      "has_torn": false,
      "timestamp": "2025-08-15T14:02:11Z"
    },
    "Verified": {
      "index": 123,
      "gender": "female",
      "age": "less_60",
      "has_torn": false,
      "timestamp": "2025-08-15T14:02:11Z"
    },
    "Accepted": {
      "index": 123,
      "gender": "female",
      "age": "less_60",
      "has_torn": false,
      "timestamp": "2025-08-15T14:02:11Z"
    }
  }
}
```

## Global Results page

image file : ./Global Results.jpg

Description: A page which shows the results of each party in the election for all poll
offices. There is a table which shows the result for the last bulletin vote. Refresh results
every 1 minute with beautiful animation to show results changes.

Endpoint

`GET /api/pollofficeresults/`

* **When `poll_office` is provided (single ID):** returns the **same schema** as before for that station.
* **When `poll_office` is omitted:** returns results **for all polling stations**.

```json
{
  "last_paper": {
    "Source 1": { "index": 250, "party_id": "ABC" },
    "Source 2": { "index": 250, "party_id": "ABC" },
    "Source ...": { "index": 250, "party_id": "ABC" },
    "Accepted": { "index": 250, "party_id": "ABC" } 
  },
  "results": [
    { "party_id": "ABC", "ballots": 120, "share": 0.48 },
    { "party_id": "DEF", "ballots": 100, "share": 0.40 },
    { "party_id": "GHI", "ballots": 30,  "share": 0.12 }
  ],
  "total_ballots": 250
}
```

## Poll Office Stats page

image file : ./Poll Office Stats.jpg

Description: A page which shows the stats of the election in a specific poll office. There
is a table "Last Vote" which shows the specific stats of the last vote. Refresh stats
every 1 minute with beautiful animation to show stats changes.

Endpoint

`GET /api/pollofficesstats/?poll_office={poll_office_id}`

* **When `poll_office` is provided (single ID):** returns the **same schema** as before for that station.
* **When `poll_office` is omitted:** returns stats **for all polling stations**.

```json
{
  "totals": {
    "total_poll_offices": 13344,
    "covered_poll_offices": 1000,
    "votes": 123,
    "male": 60,
    "female": 62,
    "less_30": 40,
    "less_60": 60,
    "more_60": 18,
    "has_torn": 7
  },
  "last_vote": {
    "Source 1": {
      "index": 123,
      "gender": "female",
      "age": "less_60",
      "has_torn": false,
      "timestamp": "2025-08-15T14:02:11Z"
    },
    "Source 2": {
      "index": 123,
      "gender": "female",
      "age": "less_60",
      "has_torn": false,
      "timestamp": "2025-08-15T14:02:11Z"
    },
    "Source ...": {
      "index": 123,
      "gender": "female",
      "age": "less_60",
      "has_torn": false,
      "timestamp": "2025-08-15T14:02:11Z"
    },
    "Verified": {
      "index": 123,
      "gender": "female",
      "age": "less_60",
      "has_torn": false,
      "timestamp": "2025-08-15T14:02:11Z"
    },
    "Accepted": {
      "index": 123,
      "gender": "female",
      "age": "less_60",
      "has_torn": false,
      "timestamp": "2025-08-15T14:02:11Z"
    }
  }
}
```

## Poll Office Results page

image file : ./Poll Office Results.jpg

Description: A page which shows the results of each party in the election for a specific poll
office. There is a table which shows the result for the last bulletin vote. Refresh results
every 1 minute with beautiful animation to show results changes.

`GET /api/pollofficeresults/?poll_office={poll_office_id}`

* **When `poll_office` is provided (single ID):** returns the **same schema** as before for that station.
* **When `poll_office` is omitted:** returns results **for all polling stations**.

```json
{
  "last_paper": {
    "Source 1": { "index": 250, "party_id": "ABC" },
    "Source 2": { "index": 250, "party_id": "ABC" },
    "Source ...": { "index": 250, "party_id": "ABC" },
    "Accepted": { "index": 250, "party_id": "ABC" } 
  },
  "results": [
    { "party_id": "ABC", "ballots": 120, "share": 0.48 },
    { "party_id": "DEF", "ballots": 100, "share": 0.40 },
    { "party_id": "GHI", "ballots": 30,  "share": 0.12 }
  ],
  "total_ballots": 250
}
```

# Stack

- Flutter
- dio

# Guidelines

- Comment the code
- Document the code
- Write tests
- Use material design
- Make the app responsive
- Use a constant BASE_API_URL for the backend base api url. Default value is "http://localhost:8000"
- Optimize for the web
- Primary color: Green, Secondary color: Red, Tertiary color: Yellow