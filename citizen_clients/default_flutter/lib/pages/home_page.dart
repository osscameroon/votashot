import 'package:flutter/material.dart';

/// Home page with 4 navigation cards.
class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final items = [
      _HomeCard(
        title: 'Global Stats',
        icon: Icons.bar_chart,
        routeName: '/global-stats',
        color: Theme.of(context).colorScheme.primary,
      ),
      _HomeCard(
        title: 'Global Results',
        icon: Icons.how_to_vote,
        routeName: '/global-results',
        color: Theme.of(context).colorScheme.secondary,
      ),
      _HomeCard(
        title: 'Poll Office Stats',
        icon: Icons.poll,
        routeName: '/select-stats',
        color: Theme.of(context).colorScheme.tertiary,
      ),
      _HomeCard(
        title: 'Poll Office Results',
        icon: Icons.fact_check,
        routeName: '/select-results',
        color: Theme.of(context).colorScheme.primary,
      ),
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('UFRECS Citizen')),
      body: LayoutBuilder(
        builder: (context, constraints) {
          final isWide = constraints.maxWidth >= 800;
          final crossAxisCount = isWide ? 4 : 2;
          return GridView.count(
            padding: const EdgeInsets.all(16),
            crossAxisCount: crossAxisCount,
            mainAxisSpacing: 16,
            crossAxisSpacing: 16,
            children: items,
          );
        },
      ),
    );
  }
}

class _HomeCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final String routeName;
  final Color color;

  const _HomeCard({
    required this.title,
    required this.icon,
    required this.routeName,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: InkWell(
        onTap: () => Navigator.of(context).pushNamed(routeName),
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 48, color: color),
              const SizedBox(height: 12),
              Text(title, style: Theme.of(context).textTheme.titleMedium),
            ],
          ),
        ),
      ),
    );
  }
}
