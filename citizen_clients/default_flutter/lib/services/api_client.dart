import 'package:dio/dio.dart';

import '../config.dart';
import '../models/poll_office.dart';
import '../models/results.dart';
import '../models/stats.dart';

/// API Client for UFRECS backend.
class ApiClient {
  final Dio _dio;

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

  /// Placeholder: fetch poll offices list. Backend endpoint not specified in docs.
  /// Replace implementation when endpoint becomes available.
  Future<List<PollOffice>> getPollOffices() async {
    // TODO: Replace with real API call when endpoint is defined.
    // Example: final resp = await _dio.get('/api/polloffices/');
    // return (resp.data as List).map((e) => PollOffice.fromJson(e)).toList();
    return const [
      PollOffice(id: 101, name: 'Central High School'),
      PollOffice(id: 102, name: 'Town Hall'),
      PollOffice(id: 103, name: 'Community Center'),
      PollOffice(id: 104, name: 'Library West'),
    ];
  }
}
