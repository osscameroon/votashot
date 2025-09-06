import 'package:flutter/material.dart';

import '../models/poll_office.dart';
import '../services/api_client.dart';

/// Selection page for Poll Office (Stats) with searchable dropdown.
class SelectPollOfficeStatsPage extends StatefulWidget {
  const SelectPollOfficeStatsPage({super.key});

  @override
  State<SelectPollOfficeStatsPage> createState() =>
      _SelectPollOfficeStatsPageState();
}

class _SelectPollOfficeStatsPageState extends State<SelectPollOfficeStatsPage> {
  final _api = ApiClient();
  late Future<List<PollOffice>> _future;

  String _query = '';
  String? _selectedIdentifier;
  PollOffice? _selected;

  @override
  void initState() {
    super.initState();
    _future = _api.getPollOffices();
  }

  void _openSelected() {
    final office = _selected;
    if (office == null) return;
    Navigator.of(context).pushNamed('/poll-office-stats', arguments: office.id);
  }

  List<PollOffice> _filtered(List<PollOffice> items) {
    final q = _query.trim().toLowerCase();
    if (q.isEmpty) return items;
    return items
        .where((e) =>
            e.name.toLowerCase().contains(q) ||
            e.identifier.toLowerCase().contains(q))
        .toList();
  }

  Widget _infoBox(PollOffice office) {
    final textTheme = Theme.of(context).textTheme;
    Widget row(String label, String? value) {
      if (value == null || value.isEmpty) return const SizedBox.shrink();
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 2),
        child: Row(
          children: [
            SizedBox(width: 120, child: Text(label, style: textTheme.bodyMedium)),
            Expanded(child: Text(value)),
          ],
        ),
      );
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: Theme.of(context).dividerColor),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(office.name, style: textTheme.titleMedium),
          const SizedBox(height: 8),
          row('Identifier', office.identifier),
          row('ID', '${office.id}'),
          row('Country', office.country),
          row('State', office.state),
          row('Region', office.region),
          row('City', office.city),
          row('County', office.county),
          row('District', office.district),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Select Poll Office (Stats)')),
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
          final filtered = _filtered(items);
          final currentValue = filtered.any(
            (e) => e.identifier == _selectedIdentifier,
          )
              ? _selectedIdentifier
              : null;

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              TextFormField(
                decoration: const InputDecoration(
                  labelText: 'Search',
                  prefixIcon: Icon(Icons.search),
                ),
                onChanged: (v) {
                  setState(() => _query = v);
                },
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                isExpanded: true,
                value: currentValue,
                decoration: const InputDecoration(
                  labelText: 'Poll Office',
                  hintText: 'Select a poll office',
                ),
                items: filtered
                    .map(
                      (e) => DropdownMenuItem<String>(
                        value: e.identifier, // value is identifier
                        child: Text(e.name), // display is name
                      ),
                    )
                    .toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedIdentifier = value;
                    _selected = items.firstWhere(
                      (e) => e.identifier == value,
                      orElse: () => items.first,
                    );
                  });
                },
              ),
              const SizedBox(height: 16),
              if (_selected != null) ...[
                _infoBox(_selected!),
                const SizedBox(height: 12),
                Align(
                  alignment: Alignment.centerRight,
                  child: ElevatedButton(
                    onPressed: _openSelected,
                    child: const Text('View Stats'),
                  ),
                ),
              ],
            ],
          );
        },
      ),
    );
  }
}
