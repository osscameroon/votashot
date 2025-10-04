import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart';

import 'config/app_config.dart';
import 'db/database.dart';
import 'l10n/app_localizations.dart';
import 'state/locale_controller.dart';
import 'state/session.dart';

/// Application entry point.
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize DB and session
  await AppDatabase.instance.init();
  await Session.instance.restore();
  await LocaleController.instance.load();

  // Optional: set default locale or load user preference
  Intl.defaultLocale = LocaleController.instance.value?.languageCode ?? 'en';

  runApp(const UfrecsApp());
}

/// Root widget configuring theme, routes and localization.
class UfrecsApp extends StatelessWidget {
  const UfrecsApp({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = ThemeData(
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppConfig.colors.primary,
        primary: AppConfig.colors.primary,
        secondary: AppConfig.colors.secondary,
        tertiary: AppConfig.colors.tertiary,
        brightness: Brightness.light,
      ),
      useMaterial3: true,
    );

    return ValueListenableBuilder<Locale?>(
      valueListenable: LocaleController.instance,
      builder: (context, locale, _) {
        return MaterialApp(
          title: 'UFRECS Reporter',
          theme: theme,
          locale: locale,
          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          supportedLocales: AppLocalizations.supportedLocales,
          onGenerateRoute: AppRouter.onGenerateRoute,
          initialRoute: Session.instance.isAuthenticated
              ? AppRouter.homeRoute
              : AppRouter.loginRoute,
        );
      },
    );
  }
}
