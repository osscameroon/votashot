import 'package:flutter/material.dart';

import 'config.dart';
import 'pages/global_results_page.dart';
import 'pages/global_stats_page.dart';
import 'pages/home_page.dart';
import 'pages/poll_office_results_page.dart';
import 'pages/poll_office_stats_page.dart';
import 'pages/select_poll_office_results_page.dart';
import 'pages/select_poll_office_stats_page.dart';

void main() {
  runApp(const UfrecsCitizenApp());
}

/// Root widget for the Ufrecs Citizen app.
class UfrecsCitizenApp extends StatelessWidget {
  const UfrecsCitizenApp({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: Colors.green,
      primary: Colors.green,
      secondary: Colors.red,
      tertiary: Colors.yellow,
      brightness: Brightness.light,
    );

    return MaterialApp(
      title: 'UFRECS Citizen',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: colorScheme,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      debugShowCheckedModeBanner: false,
      initialRoute: '/',
      routes: {
        '/': (_) => const HomePage(),
        '/global-stats': (_) => const GlobalStatsPage(),
        '/global-results': (_) => const GlobalResultsPage(),
        '/select-stats': (_) => const SelectPollOfficeStatsPage(),
        '/select-results': (_) => const SelectPollOfficeResultsPage(),
      },
      // For routes requiring arguments
      onGenerateRoute: (settings) {
        if (settings.name == '/poll-office-stats') {
          final id = settings.arguments as int;
          return MaterialPageRoute(
            builder: (_) => PollOfficeStatsPage(pollOfficeId: id),
            settings: settings,
          );
        }
        if (settings.name == '/poll-office-results') {
          final id = settings.arguments as int;
          return MaterialPageRoute(
            builder: (_) => PollOfficeResultsPage(pollOfficeId: id),
            settings: settings,
          );
        }
        return null;
      },
    );
  }
}
