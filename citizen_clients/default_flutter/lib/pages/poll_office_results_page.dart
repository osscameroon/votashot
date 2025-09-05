import 'dart:async';

import 'package:flutter/material.dart';

import '../models/results.dart';
import '../services/api_client.dart';

/// Poll Office Results page for a specific office.
class PollOfficeResultsPage extends StatefulWidget {
  final int pollOfficeId;

  const PollOfficeResultsPage({super.key, required this.pollOfficeId});

  @override
  State<PollOfficeResultsPage> createState() => _PollOfficeResultsPageState();
}

class _PollOfficeResultsPageState extends State<PollOfficeResultsPage> {
  final _api = ApiClient();
  late Future<ResultsResponse> _future;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _future = _api.getResults(pollOfficeId: widget.pollOfficeId);
    _timer = Timer.periodic(const Duration(minutes: 1), (_) => _refresh());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _refresh() {
    setState(() {
      _future = _api.getResults(pollOfficeId: widget.pollOfficeId);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Results • Office ${widget.pollOfficeId}')),
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
            return _ResultsContent(data: data);
          },
        ),
      ),
    );
  }
}

class _ResultsContent extends StatelessWidget {
  final ResultsResponse data;

  const _ResultsContent({required this.data});

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Text('Results', style: Theme.of(context).textTheme.titleLarge),
        ),
        ...data.results.map(
          (r) => ListTile(
            leading: CircleAvatar(child: Text(r.partyId.isNotEmpty ? r.partyId[0] : '?')),
            title: Text(r.partyId),
            subtitle: LinearProgressIndicator(
              value: r.share,
              color: Theme.of(context).colorScheme.primary,
              backgroundColor: Theme.of(context).colorScheme.primary.withOpacity(0.2),
            ),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                TweenAnimationBuilder<double>(
                  key: ValueKey(r.ballots),
                  tween: Tween(begin: 0, end: r.ballots.toDouble()),
                  duration: const Duration(milliseconds: 600),
                  builder: (_, v, __) => Text(v.toStringAsFixed(0)),
                ),
                Text('${(r.share * 100).toStringAsFixed(1)}%'),
              ],
            ),
          ),
        ),
        const Divider(),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0),
          child: Text('Last Paper', style: Theme.of(context).textTheme.titleLarge),
        ),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.all(16),
          child: DataTable(
            columns: const [
              DataColumn(label: Text('Source')),
              DataColumn(label: Text('Index')),
              DataColumn(label: Text('Party')),
            ],
            rows: data.lastPaper.entries
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
    );
  }
}
