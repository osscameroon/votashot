import 'package:flutter/material.dart';

import '../models/poll_office.dart';
import '../services/api_client.dart';
import '../widgets/stats_view.dart';

/// Poll Office Stats page for a specific office.
class PollOfficeStatsPage extends StatefulWidget {
  final int pollOfficeId;

  const PollOfficeStatsPage({super.key, required this.pollOfficeId});

  @override
  State<PollOfficeStatsPage> createState() => _PollOfficeStatsPageState();
}

class _PollOfficeStatsPageState extends State<PollOfficeStatsPage> {
  @override
  Widget build(BuildContext context) {
    final api = ApiClient();
    return StatsView(
      title: FutureBuilder(
        future: api.getPollOffices(),
        builder: (BuildContext context, AsyncSnapshot snapshot) {
          if (snapshot.hasData) {
            final offices = snapshot.data as List<PollOffice>;
            final PollOffice office = offices
                .where((e) => e.id == widget.pollOfficeId)
                .first;
            return Text('Stats • Office ${office.name}');
          } else if (snapshot.hasError) {
            return Icon(Icons.error_outline);
          } else {
            return CircularProgressIndicator();
          }
        },
      ),
      loadStats: () => api.getStats(pollOfficeId: widget.pollOfficeId),
      showTotalOffices: false,
      showCoveredOffices: false,
    );
  }
}
