import 'dart:async';

import 'package:flutter/material.dart';

import '../models/candidate_party.dart';
import '../models/results.dart';
import '../services/api_client.dart';

/// Reusable results page that shows totals, results list and last paper table.
/// Provide how results are fetched and the title you want in the AppBar.
class ResultsView extends StatefulWidget {
  final Widget title;
  final Future<ResultsResponse> Function() loadResults;
  final Duration refreshInterval;

  const ResultsView({
    super.key,
    required this.title,
    required this.loadResults,
    this.refreshInterval = const Duration(minutes: 1),
  });

  @override
  State<ResultsView> createState() => _ResultsViewState();
}

class _ResultsViewState extends State<ResultsView> {
  final _api = ApiClient();
  late Future<ResultsResponse> _future;
  Timer? _timer;
  Map<String, CandidateParty> _partyById = const {};

  @override
  void initState() {
    super.initState();
    _future = widget.loadResults();
    _loadCandidateParties();
    _timer = Timer.periodic(widget.refreshInterval, (_) => _refresh());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _refresh() {
    setState(() {
      _future = widget.loadResults();
    });
  }

  Future<void> _loadCandidateParties() async {
    try {
      final list = await _api.getCandidateParties();
      if (!mounted) return;
      setState(() {
        _partyById = {for (final p in list) p.identifier: p};
      });
    } catch (_) {
      // ignore and keep empty map; UI falls back to identifier
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: widget.title),
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
            return _ResultsContent(
              data: data,
              partyById: _partyById,
            );
          },
        ),
      ),
    );
  }
}

class _ResultsContent extends StatelessWidget {
  final ResultsResponse data;
  final Map<String, CandidateParty> partyById;

  const _ResultsContent({required this.data, required this.partyById});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth > 900;

        final list = _ResultsList(
          results: data.results,
          total: data.totalBallots,
          totalSources: data.totalSources,
          partyById: partyById,
        );
        final table = _LastPaperTable(entries: data.lastPaper, partyById: partyById);

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

        return ListView(
          children: [
            SizedBox(height: 400, child: list),
            const Divider(),
            table,
          ],
        );
      },
    );
  }
}

class _ResultsList extends StatelessWidget {
  final List<PartyResult> results;
  final int total;
  final int totalSources;
  final Map<String, CandidateParty> partyById;

  const _ResultsList({
    required this.results,
    required this.total,
    required this.totalSources,
    required this.partyById,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: results.length + 2,
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemBuilder: (context, index) {
        if (index == 0) {
          return ListTile(
            title: const Text('Total Ballots'),
            trailing: TweenAnimationBuilder<double>(
              key: ValueKey(total),
              tween: Tween(begin: 0, end: total.toDouble()),
              duration: const Duration(milliseconds: 600),
              builder: (_, v, __) => Text(
                v.toStringAsFixed(0),
                style: Theme.of(context).textTheme.titleLarge,
              ),
            ),
          );
        }
        if (index == 1) {
          return ListTile(
            title: const Text('Total Sources'),
            trailing: TweenAnimationBuilder<double>(
              key: ValueKey(totalSources),
              tween: Tween(begin: 0, end: totalSources.toDouble()),
              duration: const Duration(milliseconds: 600),
              builder: (_, v, __) => Text(
                v.toStringAsFixed(0),
                style: Theme.of(context).textTheme.titleLarge,
              ),
            ),
          );
        }
        final item = results[index - 2];
        return ListTile(
          leading: CircleAvatar(
            child: Text(item.partyId.isNotEmpty ? item.partyId[0] : '?'),
          ),
          title: Text(_displayName(item.partyId)),
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

  String _displayName(String partyId) {
    final p = partyById[partyId];
    if (p == null) return partyId;
    if (p.candidateName.isEmpty && p.partyName.isEmpty) return partyId;
    if (p.candidateName.isEmpty) return p.partyName;
    if (p.partyName.isEmpty) return p.candidateName;
    return '${p.candidateName} — ${p.partyName}';
  }
}

class _LastPaperTable extends StatelessWidget {
  final Map<String, LastPaperEntry> entries;
  final Map<String, CandidateParty> partyById;

  const _LastPaperTable({required this.entries, required this.partyById});

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
                DataColumn(label: Text('Party')),
              ],
              rows: entries.entries.map((e) {
                final isAccepted = e.key == 'Accepted';
                final partyId = e.value.partyId;
                final name = _displayName(partyId);
                return DataRow(
                  color: isAccepted
                      ? MaterialStateProperty.resolveWith<Color?>(
                          (states) => Colors.green.withOpacity(0.15),
                        )
                      : null,
                  cells: [
                    DataCell(Text(e.key)),
                    DataCell(Text(name)),
                  ],
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  String _displayName(String partyId) {
    final p = partyById[partyId];
    if (p == null) return partyId;
    if (p.candidateName.isEmpty && p.partyName.isEmpty) return partyId;
    if (p.candidateName.isEmpty) return p.partyName;
    if (p.partyName.isEmpty) return p.candidateName;
    return '${p.candidateName} — ${p.partyName}';
  }
}

