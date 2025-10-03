/// Poll office list and searchable API models.
class PollOffice {
  final int id;
  final String name;
  final String identifier;
  final String country;
  final String state;
  final String region;
  final String city;
  final String county;
  final String district;
  final String createdAt;
  final int votersCount;

  PollOffice({
    required this.id,
    required this.name,
    required this.identifier,
    required this.country,
    required this.state,
    required this.region,
    required this.city,
    required this.county,
    required this.district,
    required this.createdAt,
    required this.votersCount,
  });

  factory PollOffice.fromJson(Map<String, dynamic> json) => PollOffice(
        id: json['id'] as int,
        name: json['name'] as String,
        identifier: json['identifier'] as String,
        country: json['country'] as String? ?? '',
        state: json['state'] as String? ?? '',
        region: json['region'] as String? ?? '',
        city: json['city'] as String? ?? '',
        county: json['county'] as String? ?? '',
        district: json['district'] as String? ?? '',
        createdAt: json['created_at'] as String? ?? '',
        votersCount: (json['voters_count'] as num?)?.toInt() ?? 0,
      );
}

class PaginatedPollOffices {
  final int count;
  final String? next;
  final String? previous;
  final List<PollOffice> results;

  PaginatedPollOffices({
    required this.count,
    required this.next,
    required this.previous,
    required this.results,
  });

  factory PaginatedPollOffices.fromJson(Map<String, dynamic> json) =>
      PaginatedPollOffices(
        count: (json['count'] as num?)?.toInt() ?? 0,
        next: json['next'] as String?,
        previous: json['previous'] as String?,
        results: ((json['results'] as List?) ?? [])
            .map((e) => PollOffice.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}

