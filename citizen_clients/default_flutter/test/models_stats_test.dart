import 'package:flutter_test/flutter_test.dart';
import 'package:ufrecscitizen/models/stats.dart';

void main() {
  test('StatsResponse decodes sample JSON', () {
    const json = {
      "totals": {
        "total_poll_offices": 13344,
        "covered_poll_offices": 1000,
        "votes": 123,
        "male": 60,
        "female": 62,
        "less_30": 40,
        "less_60": 60,
        "more_60": 18,
        "has_torn": 7
      },
      "last_vote": {
        "Source 1": {
          "index": 123,
          "gender": "female",
          "age": "less_60",
          "has_torn": false,
          "timestamp": "2025-08-15T14:02:11Z"
        },
        "Verified": {
          "index": 124,
          "gender": "male",
          "age": "less_30",
          "has_torn": true,
          "timestamp": "2025-08-15T14:05:11Z"
        }
      }
    };

    final res = StatsResponse.fromJson(json);
    expect(res.totals.votes, 123);
    expect(res.lastVote.length, 2);
    expect(res.lastVote['Verified']!.hasTorn, true);
  });
}

