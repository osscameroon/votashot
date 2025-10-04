import 'package:flutter/material.dart';

import '../pages/home_page.dart';
// Lightweight imports at bottom to avoid cyclic issues in analysis.
import '../pages/login_page.dart';
import '../pages/poll_office_list_page.dart';
import '../pages/poll_office_minutes_page.dart';
import '../pages/results_session_page.dart';
import '../pages/settings_page.dart';
import '../pages/votes_session_page.dart';

/// Global application configuration and theme colors.
class AppConfig {
  AppConfig._();

  /// API base URL. Adjust for your backend.
  static String apiBaseUrl = const String.fromEnvironment(
    'UFRECS_API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );

  /// Static contact info rendered in settings.
  static const String contactEmail = 'contact@example.org';
  static const String contactPhone1 = '+1 555 0100';
  static const String contactPhone2 = '+1 555 0101';

  /// App color palette.
  static _Colors get colors => _Colors();
}

/// Color palette aligned with README (green, red, yellow).
class _Colors {
  final Color primary = Colors.green;
  final Color secondary = Colors.red;
  final Color tertiary = Colors.yellow.shade700;
}

/// Route names for navigation.
class AppRouter {
  AppRouter._();

  static const loginRoute = '/login';
  static const homeRoute = '/home';
  static const votesRoute = '/votes';
  static const resultsRoute = '/results';
  static const pollOfficeListRoute = '/poll_office_list';
  static const pollOfficeMinutesRoute = '/poll_office_minutes';
  static const settingsRoute = '/settings';

  static Route<dynamic> onGenerateRoute(RouteSettings settings) {
    switch (settings.name) {
      case loginRoute:
        // Deferred import to avoid circular deps in this small sample
        return MaterialPageRoute(builder: (_) => const LoginPage());
      case homeRoute:
        return MaterialPageRoute(builder: (_) => const HomePage());
      case votesRoute:
        return MaterialPageRoute(builder: (_) => const VotesSessionPage());
      case resultsRoute:
        return MaterialPageRoute(builder: (_) => const ResultsSessionPage());
      case pollOfficeListRoute:
        return MaterialPageRoute(builder: (_) => const PollOfficeListPage());
      case pollOfficeMinutesRoute:
        return MaterialPageRoute(builder: (_) => const PollOfficeMinutesPage());
      case settingsRoute:
        return MaterialPageRoute(builder: (_) => const SettingsPage());
      default:
        return MaterialPageRoute(builder: (_) => const LoginPage());
    }
  }
}
