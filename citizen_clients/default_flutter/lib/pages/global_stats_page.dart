import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../services/api_client.dart';
import '../widgets/stats_view.dart';

/// Global Stats page: shows totals and last vote table for all polling stations.
class GlobalStatsPage extends StatelessWidget {
  const GlobalStatsPage({super.key});

  @override
  Widget build(BuildContext context) {
    final api = ApiClient();
    return StatsView(
      title: const Text('Global Stats'),
      loadStats: () => api.getStats(),
    );
  }
}

/// Simple clock banner displayed below the app bar.
class _ClockBar extends StatelessWidget {
  const _ClockBar();

  @override
  Widget build(BuildContext context) {
    final textStyle = Theme.of(context).textTheme.titleMedium;
    return Material(
      color: Theme.of(context).colorScheme.surfaceVariant,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        child: Row(
          children: [
            const Icon(Icons.access_time),
            const SizedBox(width: 8),
            Expanded(
              child: StreamBuilder<DateTime>(
                stream: Stream<DateTime>.periodic(
                  const Duration(seconds: 1),
                  (_) => DateTime.now(),
                ),
                initialData: DateTime.now(),
                builder: (context, snapshot) {
                  final now = snapshot.data ?? DateTime.now();
                  final formatted = DateFormat(
                    'EEE, MMM d • HH:mm:ss',
                  ).format(now);
                  return Text(formatted, style: textStyle);
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
