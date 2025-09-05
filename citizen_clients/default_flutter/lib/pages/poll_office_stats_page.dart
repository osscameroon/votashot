import 'dart:async';

import 'package:flutter/material.dart';

import '../models/stats.dart';
import '../services/api_client.dart';

/// Poll Office Stats page for a specific office.
class PollOfficeStatsPage extends StatefulWidget {
  final int pollOfficeId;

  const PollOfficeStatsPage({super.key, required this.pollOfficeId});

  @override
  State<PollOfficeStatsPage> createState() => _PollOfficeStatsPageState();
}

class _PollOfficeStatsPageState extends State<PollOfficeStatsPage> {
  final _api = ApiClient();
  late Future<StatsResponse> _future;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _future = _api.getStats(pollOfficeId: widget.pollOfficeId);
    _timer = Timer.periodic(const Duration(minutes: 1), (_) => _refresh());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _refresh() {
    setState(() {
      _future = _api.getStats(pollOfficeId: widget.pollOfficeId);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Stats • Office ${widget.pollOfficeId}')),
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
            return _StatsContent(data: data);
          },
        ),
      ),
    );
  }
}

class _StatsContent extends StatelessWidget {
  final StatsResponse data;

  const _StatsContent({required this.data});

  @override
  Widget build(BuildContext context) {
    final totals = data.totals;
    return ListView(
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Text('Totals', style: Theme.of(context).textTheme.titleLarge),
        ),
        _AnimatedMetric(label: 'Votes', value: totals.votes),
        _AnimatedMetric(label: 'Male', value: totals.male),
        _AnimatedMetric(label: 'Female', value: totals.female),
        _AnimatedMetric(label: '< 30', value: totals.less30),
        _AnimatedMetric(label: '< 60', value: totals.less60),
        _AnimatedMetric(label: '> 60', value: totals.more60),
        _AnimatedMetric(label: 'Has Torn', value: totals.hasTorn),
        const Divider(),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0),
          child: Text('Last Vote', style: Theme.of(context).textTheme.titleLarge),
        ),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.all(16),
          child: DataTable(
            columns: const [
              DataColumn(label: Text('Source')),
              DataColumn(label: Text('Index')),
              DataColumn(label: Text('Gender')),
              DataColumn(label: Text('Age')),
              DataColumn(label: Text('Torn')),
              DataColumn(label: Text('Timestamp')),
            ],
            rows: data.lastVote.entries
                .map(
                  (e) => DataRow(cells: [
                    DataCell(Text(e.key)),
                    DataCell(Text('${e.value.index}')),
                    DataCell(Text(e.value.gender)),
                    DataCell(Text(e.value.age)),
                    DataCell(Icon(e.value.hasTorn ? Icons.check : Icons.close)),
                    DataCell(Text(e.value.timestamp.toIso8601String())),
                  ]),
                )
                .toList(),
          ),
        ),
      ],
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
        builder: (_, v, __) => Text(v.toStringAsFixed(0),
            style: Theme.of(context).textTheme.titleLarge),
      ),
    );
  }
}

