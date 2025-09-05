/// Global app configuration constants.
///
/// Use `BASE_API_URL` for the backend base API URL.
/// Override via build-time env (e.g., --dart-define) if needed.
class AppConfig {
  /// Backend base API URL. Defaults to localhost.
  static const String BASE_API_URL = String.fromEnvironment(
    'BASE_API_URL',
    defaultValue: 'http://localhost:8000',
  );
}

