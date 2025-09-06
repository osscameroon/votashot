import 'package:flutter_test/flutter_test.dart';
import 'package:ufrecscitizen/models/results.dart';

void main() {
  test('ResultsResponse decodes sample JSON', () {
    const json = {
      "last_paper": {
        "Source 1": {"index": 250, "party_id": "ABC"},
        "Accepted": {"index": 250, "party_id": "ABC"}
      },
      "results": [
        {"party_id": "ABC", "ballots": 120, "share": 0.48},
        {"party_id": "DEF", "ballots": 100, "share": 0.40},
        {"party_id": "GHI", "ballots": 30, "share": 0.12}
      ],
      "totals": {"total_ballots": 250, "total_sources": 4}
    };

    final res = ResultsResponse.fromJson(json);
    expect(res.totalBallots, 250);
    expect(res.totalSources, 4);
    expect(res.results.first.partyId, 'ABC');
    expect(res.lastPaper['Accepted']!.index, 250);
  });
}
