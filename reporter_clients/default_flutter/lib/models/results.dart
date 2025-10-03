/// Results session models (poll office results and candidate parties).
class PollOfficeResults {
  final LastPaper? lastPaper;
  final List<ResultItem> results;
  final int totalBallots;

  PollOfficeResults({
    required this.lastPaper,
    required this.results,
    required this.totalBallots,
  });

  factory PollOfficeResults.fromJson(Map<String, dynamic> json) =>
      PollOfficeResults(
        lastPaper: json['last_paper'] == null
            ? null
            : LastPaper.fromJson(json['last_paper'] as Map<String, dynamic>),
        results: ((json['results'] as List?) ?? [])
            .map((e) => ResultItem.fromJson(e as Map<String, dynamic>))
            .toList(),
        totalBallots: (json['total_ballots'] as num?)?.toInt() ?? 0,
      );
}

class LastPaper {
  final int index;
  final String partyId;
  LastPaper({required this.index, required this.partyId});
  factory LastPaper.fromJson(Map<String, dynamic> json) => LastPaper(
        index: (json['index'] as num?)?.toInt() ?? 0,
        partyId: json['party_id'] as String? ?? '',
      );
}

class ResultItem {
  final String partyId;
  final int ballots;
  final num share;
  ResultItem({required this.partyId, required this.ballots, required this.share});
  factory ResultItem.fromJson(Map<String, dynamic> json) => ResultItem(
        partyId: json['party_id'] as String? ?? '',
        ballots: (json['ballots'] as num?)?.toInt() ?? 0,
        share: (json['share'] as num?) ?? 0,
      );
}

class CandidateParty {
  final int id;
  final String partyName;
  final String candidateName;
  final String identifier;
  final String createdAt;

  CandidateParty({
    required this.id,
    required this.partyName,
    required this.candidateName,
    required this.identifier,
    required this.createdAt,
  });

  factory CandidateParty.fromJson(Map<String, dynamic> json) => CandidateParty(
        id: (json['id'] as num).toInt(),
        partyName: json['party_name'] as String? ?? '',
        candidateName: json['candidate_name'] as String? ?? '',
        identifier: json['identifier'] as String? ?? '',
        createdAt: json['created_at'] as String? ?? '',
      );
}

