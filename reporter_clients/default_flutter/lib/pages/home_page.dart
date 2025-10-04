import 'package:flutter/material.dart';

import '../config/app_config.dart';
import '../l10n/app_localizations.dart';
import '../widgets/app_bottom_nav.dart';

/// Home page with grid of cards and bottom navigation.
class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(context.l10n.appTitle),
        automaticallyImplyLeading: false, // Hide back button on Home
        backgroundColor: AppConfig.colors.primary,
        foregroundColor: Colors.white,
        elevation: 2,
      ),
      body: SafeArea(
        bottom: false,
        child: GridView.count(
          padding: const EdgeInsets.all(16),
          crossAxisCount: MediaQuery.of(context).size.width > 600 ? 3 : 2,
          mainAxisSpacing: 16,
          crossAxisSpacing: 16,
          children: [
            _HomeCard(
              icon: Icons.how_to_vote,
              label: context.l10n.homeVotes,
              color: AppConfig.colors.primary,
              onTap: () => Navigator.of(
                context,
              ).pushReplacementNamed(AppRouter.votesRoute),
            ),
            _HomeCard(
              icon: Icons.ballot,
              label: context.l10n.homeResults,
              color: AppConfig.colors.tertiary,
              onTap: () => Navigator.of(
                context,
              ).pushReplacementNamed(AppRouter.resultsRoute),
            ),
            _HomeCard(
              icon: Icons.list,
              label: context.l10n.homeList,
              color: AppConfig.colors.secondary,
              onTap: () => Navigator.of(
                context,
              ).pushReplacementNamed(AppRouter.pollOfficeListRoute),
            ),
            _HomeCard(
              icon: Icons.summarize,
              label: context.l10n.homeMinutes,
              color: Colors.blue,
              onTap: () => Navigator.of(
                context,
              ).pushReplacementNamed(AppRouter.pollOfficeMinutesRoute),
            ),
            _HomeCard(
              icon: Icons.settings,
              label: context.l10n.homeSettings,
              color: Colors.blueGrey,
              onTap: () => Navigator.of(
                context,
              ).pushReplacementNamed(AppRouter.settingsRoute),
            ),
          ],
        ),
      ),
      bottomNavigationBar: const AppBottomNav(currentIndex: 0),
    );
  }
}

class _HomeCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;
  const _HomeCard({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: InkWell(
        onTap: onTap,
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 40, color: color),
              const SizedBox(height: 12),
              Text(
                label,
                style: Theme.of(context).textTheme.titleMedium,
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
