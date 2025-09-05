import 'dart:async';

import 'package:flutter/material.dart';

import '../models/results.dart';
import '../services/api_client.dart';

/// Global Results page: shows party results and last paper table.
class GlobalResultsPage extends StatefulWidget {
  const GlobalResultsPage({super.key});

  @override
  State<GlobalResultsPage> createState() => _GlobalResultsPageState();
}

class _GlobalResultsPageState extends State<GlobalResultsPage> {
  final _api = ApiClient();
  late Future<ResultsResponse> _future;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _future = _api.getResults();
    _timer = Timer.periodic(const Duration(minutes: 1), (_) => _refresh());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _refresh() {
    setState(() {
      _future = _api.getResults();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Global Results')),
      body: RefreshIndicator(
        onRefresh: () async => _refresh(),
        child: FutureBuilder<ResultsResponse>(
          future: _future,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text('Failed to load results: ${snapshot.error}'),
                ),
              );
            }
            final data = snapshot.data!;
            return _ResultsContent(data: data, onRetry: _refresh);
          },
        ),
      ),
    );
  }
}

class _ResultsContent extends StatelessWidget {
  final ResultsResponse data;
  final VoidCallback onRetry;

  const _ResultsContent({required this.data, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth > 900;

        final list = _ResultsList(results: data.results, total: data.totalBallots);
        final table = _LastPaperTable(entries: data.lastPaper);

        if (isWide) {
          return Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(child: list),
              const VerticalDivider(width: 1),
              Expanded(child: table),
            ],
          );
        }

        return ListView(children: [SizedBox(height: 400, child: list), const Divider(), table]);
      },
    );
  }
}

class _ResultsList extends StatelessWidget {
  final List<PartyResult> results;
  final int total;

  const _ResultsList({required this.results, required this.total});

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: results.length + 1,
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemBuilder: (context, index) {
        if (index == 0) {
          return ListTile(
            title: const Text('Total Ballots'),
            trailing: TweenAnimationBuilder<double>(
              key: ValueKey(total),
              tween: Tween(begin: 0, end: total.toDouble()),
              duration: const Duration(milliseconds: 600),
              builder: (_, v, __) => Text(v.toStringAsFixed(0),
                  style: Theme.of(context).textTheme.titleLarge),
            ),
          );
        }
        final item = results[index - 1];
        return ListTile(
          leading: CircleAvatar(child: Text(item.partyId.isNotEmpty ? item.partyId[0] : '?')),
          title: Text(item.partyId),
          subtitle: LinearProgressIndicator(
            value: item.share,
            color: Theme.of(context).colorScheme.primary,
            backgroundColor: Theme.of(context).colorScheme.primary.withOpacity(0.2),
          ),
          trailing: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              TweenAnimationBuilder<double>(
                key: ValueKey(item.ballots),
                tween: Tween(begin: 0, end: item.ballots.toDouble()),
                duration: const Duration(milliseconds: 600),
                builder: (_, v, __) => Text(v.toStringAsFixed(0)),
              ),
              Text('${(item.share * 100).toStringAsFixed(1)}%'),
            ],
          ),
        );
      },
    );
  }
}

class _LastPaperTable extends StatelessWidget {
  final Map<String, LastPaperEntry> entries;

  const _LastPaperTable({required this.entries});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Last Paper', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 12),
          Container(
            decoration: BoxDecoration(
              border: Border.all(color: Theme.of(context).dividerColor),
              borderRadius: BorderRadius.circular(8),
            ),
            child: DataTable(
              columns: const [
                DataColumn(label: Text('Source')),
                DataColumn(label: Text('Index')),
                DataColumn(label: Text('Party')),
              ],
              rows: entries.entries
                  .map(
                    (e) => DataRow(cells: [
                      DataCell(Text(e.key)),
                      DataCell(Text('${e.value.index}')),
                      DataCell(Text(e.value.partyId)),
                    ]),
                  )
                  .toList(),
            ),
          ),
        ],
      ),
    );
  }
}
