# UFRECS Citizen App

Flutter app connecting to the UFRECS backend to display live election stats and results.

## Features

- Home with 4 cards: Global Stats, Global Results, Poll Office Stats, Poll Office Results
- Global and per-poll-office views for stats and results
- Auto-refresh every 1 minute with smooth animations for changing values
- Material 3 theme (Primary: Green, Secondary: Red, Tertiary: Yellow)
- Responsive layout optimized for web and mobile

## Configuration

- Backend base URL: set `BASE_API_URL` (defaults to `http://localhost:8000`).
  - Example: `flutter run --dart-define=BASE_API_URL=https://api.example.com`

## Run

1. Install dependencies: `flutter pub get`
2. Start the app: `flutter run -d chrome` (for web) or any device

## Endpoints used

- `GET /api/pollofficesstats/` and `GET /api/pollofficesstats/?poll_office={id}`
- `GET /api/pollofficeresults/` and `GET /api/pollofficeresults/?poll_office={id}`

Note: Poll offices list endpoint is not specified in docs; the app currently shows a mocked list on the selection pages. Replace `ApiClient.getPollOffices()` implementation when the endpoint is available.

## Tests

- Model decoding tests for stats and results
- Widget smoke test for Home page

Run: `flutter test`
