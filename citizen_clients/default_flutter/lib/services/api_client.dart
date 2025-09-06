import 'package:dio/dio.dart';

import '../config.dart';
import '../models/poll_office.dart';
import '../models/results.dart';
import '../models/stats.dart';
import '../models/candidate_party.dart';

/// API Client for UFRECS backend.
class ApiClient {
  final Dio _dio;
  static List<PollOffice>? _pollOfficesCache;
  static List<CandidateParty>? _candidatePartiesCache;

  ApiClient._(this._dio);

  factory ApiClient() {
    final dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.BASE_API_URL,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      ),
    );
    return ApiClient._(dio);
  }

  /// Testing/advanced: create client with a provided Dio instance.
  factory ApiClient.withDio(Dio dio) => ApiClient._(dio);

  /// GET /api/pollofficesstats/ or /api/pollofficesstats/?poll_office={id}
  Future<StatsResponse> getStats({int? pollOfficeId}) async {
    final path = '/api/pollofficestats/';
    final resp = await _dio.get(
      path,
      queryParameters: {if (pollOfficeId != null) 'poll_office': pollOfficeId},
    );
    return StatsResponse.fromJson(resp.data as Map<String, dynamic>);
  }

  /// GET /api/pollofficeresults/ or /api/pollofficeresults/?poll_office={id}
  Future<ResultsResponse> getResults({int? pollOfficeId}) async {
    final path = '/api/pollofficeresults/';
    final resp = await _dio.get(
      path,
      queryParameters: {if (pollOfficeId != null) 'poll_office': pollOfficeId},
    );
    return ResultsResponse.fromJson(resp.data as Map<String, dynamic>);
  }

  /// GET /api/polloffices/ with limit-offset pagination.
  /// Caches results in-memory since poll offices are static.
  Future<List<PollOffice>> getPollOffices() async {
    // Return cached list if already fetched since poll offices don't change
    final cached = _pollOfficesCache;
    if (cached != null && cached.isNotEmpty) return cached;

    const limit = 1000; // page size
    var offset = 0;
    final List<PollOffice> all = [];
    String? next;

    do {
      final resp = await _dio.get(
        '/api/polloffices/',
        queryParameters: {'limit': limit, 'offset': offset},
      );

      final data = resp.data as Map<String, dynamic>;
      final results = (data['results'] as List<dynamic>? ?? const []);
      all.addAll(
        results.map((e) => PollOffice.fromJson(e as Map<String, dynamic>)),
      );

      next = data['next'] as String?; // full URL or null
      offset += results.length; // move offset by fetched items

      if (results.isEmpty) break; // safety stop
    } while (next != null);

    _pollOfficesCache = all;
    return all;
  }

  /// GET /api/candidateparties/ with limit-offset pagination.
  /// Caches results in-memory since candidate parties are static during the event.
  Future<List<CandidateParty>> getCandidateParties() async {
    final cached = _candidatePartiesCache;
    if (cached != null && cached.isNotEmpty) return cached;

    const limit = 100;
    var offset = 0;
    final List<CandidateParty> all = [];
    String? next;

    do {
      final resp = await _dio.get(
        '/api/candidateparties/',
        queryParameters: {
          'limit': limit,
          'offset': offset,
        },
      );

      final data = resp.data as Map<String, dynamic>;
      final results = (data['results'] as List<dynamic>? ?? const []);
      all.addAll(
        results.map((e) =>
            CandidateParty.fromJson(e as Map<String, dynamic>)),
      );

      next = data['next'] as String?;
      offset += results.length;

      if (results.isEmpty) break;
    } while (next != null);

    _candidatePartiesCache = all;
    return all;
  }
}
