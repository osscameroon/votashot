import 'dart:async';

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/stats.dart';
import '../services/api_client.dart';

/// Global Stats page: shows totals and last vote table for all polling stations.
class GlobalStatsPage extends StatefulWidget {
  const GlobalStatsPage({super.key});

  @override
  State<GlobalStatsPage> createState() => _GlobalStatsPageState();
}

class _GlobalStatsPageState extends State<GlobalStatsPage> {
  final _api = ApiClient();
  late Future<StatsResponse> _future;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _future = _api.getStats();
    _timer = Timer.periodic(const Duration(minutes: 1), (_) => _refresh());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _refresh() {
    setState(() {
      _future = _api.getStats();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Global Stats')),
      body: RefreshIndicator(
        onRefresh: () async => _refresh(),
        child: FutureBuilder<StatsResponse>(
          future: _future,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text('Failed to load stats: ${snapshot.error}'),
                ),
              );
            }
            final data = snapshot.data!;
            return _StatsContent(data: data, onRetry: _refresh);
          },
        ),
      ),
    );
  }
}

class _StatsContent extends StatelessWidget {
  final StatsResponse data;
  final VoidCallback onRetry;

  const _StatsContent({required this.data, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    final totals = data.totals;
    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth > 900;
        final side = Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(
                'Totals',
                style: Theme.of(context).textTheme.titleLarge,
              ),
            ),
            _AnimatedMetric(
              label: 'Total Poll Offices',
              value: totals.totalPollOffices,
            ),
            _AnimatedMetric(
              label: 'Covered Poll Offices',
              value: totals.coveredPollOffices,
            ),
            _AnimatedMetric(label: 'Votes', value: totals.votes),
            _AnimatedMetric(label: 'Male', value: totals.male),
            _AnimatedMetric(label: 'Female', value: totals.female),
            _AnimatedMetric(label: '< 30', value: totals.less30),
            _AnimatedMetric(label: '< 60', value: totals.less60),
            _AnimatedMetric(label: '> 60', value: totals.more60),
            _AnimatedMetric(label: 'Has Torn', value: totals.hasTorn),
          ],
        );

        final table = _LastVoteTable(entries: data.lastVote);

        if (isWide) {
          return Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(width: 380, child: side),
              const VerticalDivider(width: 1),
              Expanded(child: table),
            ],
          );
        }

        return ListView(
          children: [
            side,
            const Divider(height: 1),
            SizedBox(height: 400, child: table),
          ],
        );
      },
    );
  }
}

class _AnimatedMetric extends StatelessWidget {
  final String label;
  final int value;

  const _AnimatedMetric({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(label),
      trailing: TweenAnimationBuilder<double>(
        key: ValueKey(value),
        tween: Tween(begin: 0, end: value.toDouble()),
        duration: const Duration(milliseconds: 600),
        curve: Curves.easeOut,
        builder: (_, v, __) => Text(
          v.toStringAsFixed(0),
          style: Theme.of(context).textTheme.titleLarge,
        ),
      ),
    );
  }
}

class _LastVoteTable extends StatelessWidget {
  final Map<String, LastVoteEntry> entries;

  const _LastVoteTable({required this.entries});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Last Vote', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 12),
          Container(
            decoration: BoxDecoration(
              border: Border.all(color: Theme.of(context).dividerColor),
              borderRadius: BorderRadius.circular(8),
            ),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 8),
              child: DataTable(
                columns: const [
                  DataColumn(label: Text('Source')),
                  DataColumn(label: Text('Index')),
                  DataColumn(label: Text('Gender')),
                  DataColumn(label: Text('Age')),
                  DataColumn(label: Text('Torn')),
                  DataColumn(label: Text('Hour')),
                ],
                rows: entries.entries.map((e) {
                  // Conditional row background and text color based on source
                  Color? bg;
                  Color? fg;
                  if (e.key == 'Accepted') {
                    bg = Colors.green;
                    fg = Colors.white;
                  } else if (e.key == 'Verified') {
                    bg = Colors.blue;
                    fg = Colors.white;
                  }

                  TextStyle? textStyle = fg != null ? TextStyle(color: fg) : null;

                  return DataRow(
                    color: bg != null
                        ? MaterialStateProperty.resolveWith<Color?>((states) => bg)
                        : null,
                    cells: [
                      DataCell(Text(e.key, style: textStyle)),
                      DataCell(Text('${e.value.index}', style: textStyle)),
                      DataCell(Text(e.value.gender, style: textStyle)),
                      DataCell(Text(e.value.age, style: textStyle)),
                      DataCell(
                        Icon(
                          e.value.hasTorn ? Icons.check : Icons.close,
                          color: fg ??
                              (e.value.hasTorn
                                  ? Theme.of(context).colorScheme.secondary
                                  : Theme.of(context).disabledColor),
                        ),
                      ),
                      DataCell(
                        Text(
                          DateFormat('HH:mm').format(e.value.timestamp),
                          style: textStyle,
                        ),
                      ),
                    ],
                  );
                }).toList(),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
