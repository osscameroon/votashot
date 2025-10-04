import 'package:flutter/material.dart';

import '../config/app_config.dart';
import '../l10n/app_localizations.dart';

/// Reusable bottom navigation used across all pages except Login.
class AppBottomNav extends StatelessWidget {
  final int currentIndex;

  const AppBottomNav({super.key, required this.currentIndex});

  void _navigate(BuildContext context, int index) {
    switch (index) {
      case 0:
        Navigator.of(context).pushReplacementNamed(AppRouter.homeRoute);
        break;
      case 1:
        Navigator.of(context).pushReplacementNamed(AppRouter.votesRoute);
        break;
      case 2:
        Navigator.of(context).pushReplacementNamed(AppRouter.resultsRoute);
        break;
      case 3:
        Navigator.of(context).pushReplacementNamed(AppRouter.settingsRoute);
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: BottomNavigationBar(
        currentIndex: currentIndex,
        backgroundColor: Theme.of(context).colorScheme.surfaceVariant,
        selectedItemColor: AppConfig.colors.primary,
        unselectedItemColor: Colors.grey,
        showUnselectedLabels: true,
        elevation: 8,
        onTap: (i) => _navigate(context, i),
        items: [
          BottomNavigationBarItem(icon: const Icon(Icons.home), label: context.l10n.homeHome),
          BottomNavigationBarItem(icon: const Icon(Icons.how_to_vote), label: context.l10n.homeVotes),
          BottomNavigationBarItem(icon: const Icon(Icons.ballot), label: context.l10n.homeResults),
          BottomNavigationBarItem(icon: const Icon(Icons.settings), label: context.l10n.homeSettings),
        ],
      ),
    );
  }
}
