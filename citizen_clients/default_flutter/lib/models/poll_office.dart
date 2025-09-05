/// Simple Poll Office entity for select pages.
class PollOffice {
  final int id;
  final String name;

  const PollOffice({required this.id, required this.name});

  factory PollOffice.fromJson(Map<String, dynamic> json) =>
      PollOffice(id: (json['id'] ?? 0) as int, name: (json['name'] ?? '') as String);
}

