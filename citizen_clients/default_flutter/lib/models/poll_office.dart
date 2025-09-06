/// Simple Poll Office entity for select pages.
class PollOffice {
  final int id;
  final String name;
  final String identifier;
  final String country;
  final String? state;
  final String? region;
  final String? city;
  final String? county;
  final String? district;

  const PollOffice({
    required this.id,
    required this.name,
    required this.identifier,
    required this.country,
    this.state,
    this.region,
    this.city,
    this.county,
    this.district,
  });

  factory PollOffice.fromJson(Map<String, dynamic> json) => PollOffice(
    id: (json['id'] ?? 0) as int,
    name: (json['name'] ?? '') as String,
    identifier: (json['identifier'] ?? '') as String,
    country: (json['country'] ?? '') as String,
    state: (json['state']) as String?,
    region: (json['region']) as String?,
    city: (json['city']) as String?,
    county: (json['county']) as String?,
    district: (json['district']) as String?,
  );
}
