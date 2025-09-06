import 'package:flutter/material.dart';

import '../services/api_client.dart';
import '../widgets/results_view.dart';

/// Poll Office Results page for a specific office.
class PollOfficeResultsPage extends StatefulWidget {
  final int pollOfficeId;

  const PollOfficeResultsPage({super.key, required this.pollOfficeId});

  @override
  State<PollOfficeResultsPage> createState() => _PollOfficeResultsPageState();
}

class _PollOfficeResultsPageState extends State<PollOfficeResultsPage> {
  final _api = ApiClient();
  String? _officeName;

  @override
  void initState() {
    super.initState();
    _loadOfficeName();
  }

  Future<void> _loadOfficeName() async {
    try {
      final offices = await _api.getPollOffices();
      final office = offices.firstWhere(
        (o) => o.id == widget.pollOfficeId,
        orElse: () => offices.first,
      );
      setState(() => _officeName = office.name);
    } catch (_) {
      // ignore; fallback to ID in title
    }
  }

  @override
  Widget build(BuildContext context) {
    final titleText = _officeName != null
        ? 'Results • ${_officeName!}'
        : 'Results • Office ${widget.pollOfficeId}';
    return ResultsView(
      title: Text(titleText),
      loadResults: () => _api.getResults(pollOfficeId: widget.pollOfficeId),
    );
  }
}
