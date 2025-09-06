class CandidateParty {
  final int id;
  final String partyName;
  final String candidateName;
  final String identifier;
  final DateTime? createdAt;

  const CandidateParty({
    required this.id,
    required this.partyName,
    required this.candidateName,
    required this.identifier,
    this.createdAt,
  });

  factory CandidateParty.fromJson(Map<String, dynamic> json) => CandidateParty(
        id: (json['id'] ?? 0) as int,
        partyName: (json['party_name'] ?? '') as String,
        candidateName: (json['candidate_name'] ?? '') as String,
        identifier: (json['identifier'] ?? '') as String,
        createdAt: DateTime.tryParse((json['created_at'] ?? '') as String),
      );
}

