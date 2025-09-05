import 'dart:convert';

/// Single last paper item from a source label.
class LastPaperEntry {
  final int index;
  final String partyId;

  const LastPaperEntry({
    required this.index,
    required this.partyId,
  });

  factory LastPaperEntry.fromJson(Map<String, dynamic> json) => LastPaperEntry(
        index: (json['index'] ?? 0) as int,
        partyId: (json['party_id'] ?? '') as String,
      );
}

/// Aggregated results for a single party.
class PartyResult {
  final String partyId;
  final int ballots;
  final double share; // 0..1

  const PartyResult({
    required this.partyId,
    required this.ballots,
    required this.share,
  });

  factory PartyResult.fromJson(Map<String, dynamic> json) => PartyResult(
        partyId: (json['party_id'] ?? '') as String,
        ballots: (json['ballots'] ?? 0) as int,
        share: ((json['share'] ?? 0.0) as num).toDouble(),
      );
}

/// Response payload for results endpoints.
class ResultsResponse {
  final Map<String, LastPaperEntry> lastPaper;
  final List<PartyResult> results;
  final int totalBallots;

  const ResultsResponse({
    required this.lastPaper,
    required this.results,
    required this.totalBallots,
  });

  factory ResultsResponse.fromJson(Map<String, dynamic> json) {
    final lp = <String, LastPaperEntry>{};
    final raw = (json['last_paper'] ?? const {}) as Map<String, dynamic>;
    for (final entry in raw.entries) {
      if (entry.value is Map<String, dynamic>) {
        lp[entry.key] = LastPaperEntry.fromJson(entry.value as Map<String, dynamic>);
      }
    }
    final results = ((json['results'] ?? const []) as List)
        .whereType<Map<String, dynamic>>()
        .map(PartyResult.fromJson)
        .toList(growable: false);
    final total = (json['total_ballots'] ?? 0) as int;
    return ResultsResponse(lastPaper: lp, results: results, totalBallots: total);
  }

  static ResultsResponse decode(String source) =>
      ResultsResponse.fromJson(json.decode(source) as Map<String, dynamic>);
}

