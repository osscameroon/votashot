import 'package:flutter/material.dart';

import '../services/api_client.dart';
import '../widgets/results_view.dart';

/// Global Results page using the reusable ResultsView.
class GlobalResultsPage extends StatelessWidget {
  const GlobalResultsPage({super.key});

  @override
  Widget build(BuildContext context) {
    final api = ApiClient();
    return ResultsView(
      title: const Text('Global Results'),
      loadResults: () => api.getResults(),
    );
  }
}
