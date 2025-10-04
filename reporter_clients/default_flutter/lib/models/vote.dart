/// Vote form payload and stats models.
class VotePayload {
  final int index;
  final String gender; // 'male' | 'female'
  final String age; // 'less_30' | 'less_60' | 'more_60'
  final bool hasTorn;

  VotePayload({
    required this.index,
    required this.gender,
    required this.age,
    required this.hasTorn,
  });

  Map<String, dynamic> toJson() => {
    'index': index,
    'gender': gender,
    'age': age,
    'has_torn': hasTorn,
  };
}

class VoteResponse {
  final int id;
  final int index;
  VoteResponse(this.id, this.index);
  factory VoteResponse.fromJson(Map<String, dynamic> json) =>
      VoteResponse((json['id'] as num).toInt(), (json['index'] as num).toInt());
}

class VoteStats {
  final Map<String, int> genders;
  final Map<String, int> ages;
  final LastVote? lastVote;

  VoteStats({
    required this.genders,
    required this.ages,
    required this.lastVote,
  });

  factory VoteStats.fromJson(Map<String, dynamic> json) {
    return VoteStats(
      genders: Map<String, int>.from(
        (json['genders'] ?? {}).map(
          (k, v) => MapEntry<String, int>(k as String, (v as num).toInt()),
        ),
      ),
      ages: Map<String, int>.from(
        (json['ages'] ?? {}).map(
          (k, v) => MapEntry<String, int>(k as String, (v as num).toInt()),
        ),
      ),
      lastVote: json['last_vote'] == null
          ? null
          : LastVote.fromJson(
              json['last_vote']['Accepted'] as Map<String, dynamic>,
            ),
    );
  }
}

class LastVote {
  final int index;
  final String gender;
  final String age;
  final bool hasTorn;

  LastVote({
    required this.index,
    required this.gender,
    required this.age,
    required this.hasTorn,
  });

  factory LastVote.fromJson(Map<String, dynamic> json) => LastVote(
    index: (json['index'] as num?)?.toInt() ?? 0,
    gender: json['gender'] as String? ?? '',
    age: json['age'] as String? ?? '',
    hasTorn: (json['has_torn'] as bool),
  );
}
