# UFRECS Citizen Client

An UFRECS citizen client is any application that connects to an UFRECS backend to provide
realtime data (stats and results).

The client provides 3 modes: Stats mode, Results mode and I-Vote mode.

## 1. Modes

### Stats mode

The Stats mode is a mode where the client shows the stats about the ongoing election.
The stats can be displayed globally or per poll office. The user must be
shown an option to switch from a global view to a poll-office view.

In this mode the app uses the endpoint `GET /api/pollofficesstats/?poll_office={poll_office_id}`
to get the stats.


### Results mode

The Stats mode is a mode where the client shows the results of the ongoing election.
The results can be displayed globally or per poll office. The user must be
shown an option to switch from a global view to a poll-office view.
The results here are the paper vote count.

In this mode the app uses the endpoint `GET /api/pollofficeresults/?poll_office={poll_office_id}`
to get the results.

### I-Vote mode

I-Vote mode is a mode where the user indicates he is currently voting.
The client must start a websocket connection to `WS /ws/vote-verification`. Listen for the vote's report
the reporters/source in the poll office will do. Then confirms that the proposed informations
are correct. Then switch back to stats mode.

## 2. Implementations

You can use whatever technologies you want. The application can be in any form
be it a mobile app, a bot or a website.

## 3. Guidelines

The application must be very accessible. Any person with basic knowledge must be able to use.
The rule of 3 clicks must be respected. The UI must be self explanatory.