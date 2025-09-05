import 'dart:convert';

/// Totals for stats across polling offices or a single office.
class StatsTotals {
  final int totalPollOffices;
  final int coveredPollOffices;
  final int votes;
  final int male;
  final int female;
  final int less30;
  final int less60;
  final int more60;
  final int hasTorn;

  const StatsTotals({
    required this.totalPollOffices,
    required this.coveredPollOffices,
    required this.votes,
    required this.male,
    required this.female,
    required this.less30,
    required this.less60,
    required this.more60,
    required this.hasTorn,
  });

  factory StatsTotals.fromJson(Map<String, dynamic> json) => StatsTotals(
    totalPollOffices: (json['total_poll_offices'] ?? 0) as int,
    coveredPollOffices: (json['covered_poll_offices'] ?? 0) as int,
    votes: (json['votes'] ?? 0) as int,
    male: (json['male'] ?? 0) as int,
    female: (json['female'] ?? 0) as int,
    less30: (json['less_30'] ?? 0) as int,
    less60: (json['less_60'] ?? 0) as int,
    more60: (json['more_60'] ?? 0) as int,
    hasTorn: (json['has_torn'] ?? 0) as int,
  );
}

/// Single last vote item from a source label.
class LastVoteEntry {
  final int index;
  final String gender; // e.g., 'female' | 'male'
  final String age; // e.g., 'less_60'
  final bool hasTorn;
  final DateTime timestamp;

  const LastVoteEntry({
    required this.index,
    required this.gender,
    required this.age,
    required this.hasTorn,
    required this.timestamp,
  });

  factory LastVoteEntry.fromJson(Map<String, dynamic> json) => LastVoteEntry(
    index: (json['index'] ?? 0) as int,
    gender: (json['gender'] ?? '') as String,
    age: (json['age'] ?? '') as String,
    hasTorn: (json['has_torn'] ?? false) as bool,
    timestamp:
        DateTime.tryParse((json['created_at'] ?? '') as String) ??
        DateTime.fromMillisecondsSinceEpoch(0, isUtc: true),
  );
}

/// Response payload for stats endpoints.
class StatsResponse {
  final StatsTotals totals;
  final Map<String, LastVoteEntry> lastVote;

  const StatsResponse({required this.totals, required this.lastVote});

  factory StatsResponse.fromJson(Map<String, dynamic> json) {
    final totals = StatsTotals.fromJson(
      (json['totals'] ?? const {}) as Map<String, dynamic>,
    );
    final lv = <String, LastVoteEntry>{};
    final raw = (json['last_vote'] ?? const {}) as Map<dynamic, dynamic>;
    for (final entry in raw.entries) {
      if (entry.value is Map<String, dynamic>) {
        lv[entry.key] = LastVoteEntry.fromJson(
          entry.value as Map<String, dynamic>,
        );
      }
    }
    return StatsResponse(totals: totals, lastVote: lv);
  }

  static StatsResponse decode(String source) =>
      StatsResponse.fromJson(json.decode(source) as Map<String, dynamic>);
}
