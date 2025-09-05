import 'package:flutter/material.dart';

import '../models/poll_office.dart';
import '../services/api_client.dart';

/// Selection page for Poll Office (Results).
class SelectPollOfficeResultsPage extends StatefulWidget {
  const SelectPollOfficeResultsPage({super.key});

  @override
  State<SelectPollOfficeResultsPage> createState() => _SelectPollOfficeResultsPageState();
}

class _SelectPollOfficeResultsPageState extends State<SelectPollOfficeResultsPage> {
  final _api = ApiClient();
  late Future<List<PollOffice>> _future;

  @override
  void initState() {
    super.initState();
    _future = _api.getPollOffices();
  }

  void _open(PollOffice office) {
    Navigator.of(context).pushNamed('/poll-office-results', arguments: office.id);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Select Poll Office (Results)')),
      body: FutureBuilder<List<PollOffice>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Text('Failed to load poll offices: ${snapshot.error}'),
              ),
            );
          }
          final items = snapshot.data!;
          return ListView.separated(
            padding: const EdgeInsets.all(8),
            itemCount: items.length,
            separatorBuilder: (_, __) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final office = items[index];
              return ListTile(
                title: Text(office.name),
                subtitle: Text('ID: ${office.id}'),
                trailing: ElevatedButton(
                  onPressed: () => _open(office),
                  child: const Text('View Results'),
                ),
              );
            },
          );
        },
      ),
    );
  }
}

