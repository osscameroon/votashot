import 'package:dio/dio.dart';
import 'package:dio_smart_retry/dio_smart_retry.dart';
import 'package:flutter/foundation.dart';

import '../config/app_config.dart';
import '../models/auth.dart';
import '../models/poll_office.dart';
import '../models/results.dart';
import '../models/vote.dart';
import '../state/session.dart';

/// API client using Dio with retry and auth header injection.
class ApiClient {
  ApiClient._() {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.apiBaseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 20),
        sendTimeout: const Duration(seconds: 20),
      ),
    );

    // Minimal auth header injection
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (opts, handler) {
          final token = Session.instance.token;
          if (token != null && token.isNotEmpty) {
            opts.headers['Authorization'] = 'Bearer $token';
          }
          // Track request start time for duration metrics
          opts.extra['__startTime'] = DateTime.now();
          handler.next(opts);
        },
        onResponse: (res, handler) {
          if (kDebugMode) {
            final started =
                res.requestOptions.extra['__startTime'] as DateTime?;
            final dur = started != null
                ? DateTime.now().difference(started).inMilliseconds
                : null;
            debugPrint(
              '[HTTP] ${res.requestOptions.method} ${res.requestOptions.uri} -> ${res.statusCode}${dur != null ? ' (${dur}ms)' : ''}',
            );
          }
          handler.next(res);
        },
        onError: (err, handler) {
          if (kDebugMode) {
            final started =
                err.requestOptions.extra['__startTime'] as DateTime?;
            final dur = started != null
                ? DateTime.now().difference(started).inMilliseconds
                : null;
            debugPrint(
              '[HTTP ERROR] ${err.requestOptions.method} ${err.requestOptions.uri} -> ${err.response?.statusCode} ${err.type}${dur != null ? ' (${dur}ms)' : ''}: ${err.message}',
            );
          }
          handler.next(err);
        },
      ),
    );

    _dio.interceptors.add(
      RetryInterceptor(
        dio: _dio,
        retries: 3,
        retryDelays: const [
          Duration(milliseconds: 500),
          Duration(seconds: 1),
          Duration(seconds: 2),
        ],
        logPrint: (obj) {
          if (kDebugMode) debugPrint('[DioRetry] $obj');
        },
      ),
    );

    // Verbose request/response logging in debug mode, without sensitive headers
    if (kDebugMode) {
      _dio.interceptors.add(
        LogInterceptor(
          request: true,
          requestHeader: false, // avoid leaking Authorization header
          requestBody: true,
          responseHeader: false,
          responseBody: false,
          error: true,
          logPrint: (obj) => debugPrint(obj.toString()),
        ),
      );
    }
  }

  static final ApiClient instance = ApiClient._();
  late final Dio _dio;

  /// Authenticate elector and store session.
  Future<AuthenticateResponse> authenticate({
    required String electorId,
    required String pollOfficeId,
    required String? password,
  }) async {
    final res = await _dio.post(
      '/api/authenticate/',
      data: {
        'elector_id': electorId,
        'password': password ?? '',
        'poll_office_id': pollOfficeId,
      },
    );
    final auth = AuthenticateResponse.fromJson(
      res.data as Map<String, dynamic>,
    );
    Session.instance
      ..token = auth.token
      ..electorId = electorId
      ..pollOfficeId = auth.pollOfficeId
      ..s3 = auth.s3;
    await Session.instance.persist();
    return auth;
  }

  /// Search poll offices by query (min 3 chars recommended).
  Future<List<PollOffice>> searchPollOffices(String q) async {
    if (q.trim().length < 3) return [];
    final res = await _dio.get(
      '/api/polloffices/',
      queryParameters: {'search': q},
    );
    final page = PaginatedPollOffices.fromJson(
      res.data as Map<String, dynamic>,
    );
    return page.results;
  }

  /// Fetch vote stats for a poll office.
  Future<VoteStats> getPollOfficeStats(String pollOfficeId) async {
    final res = await _dio.get(
      '/api/pollofficestats/?poll_office=$pollOfficeId',
    );
    return VoteStats.fromJson(res.data as Map<String, dynamic>);
  }

  /// Submit a vote.
  Future<VoteResponse> submitVote(VotePayload payload) async {
    final res = await _dio.post('/api/vote/', data: payload.toJson());
    return VoteResponse.fromJson(res.data as Map<String, dynamic>);
  }

  /// Poll office results summary.
  Future<PollOfficeResults> getPollOfficeResults(String pollOfficeId) async {
    final res = await _dio.get(
      '/api/pollofficeresults/?poll_office=$pollOfficeId',
    );
    return PollOfficeResults.fromJson(res.data as Map<String, dynamic>);
  }

  /// Candidate parties list.
  Future<List<CandidateParty>> getCandidateParties() async {
    final res = await _dio.get('/api/candidateparties/');
    final data = res.data as Map<String, dynamic>;
    final results = (data['results'] as List?) ?? [];
    return results
        .map((e) => CandidateParty.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// Refresh S3 temporary credentials and update the session.
  /// Returns the new credentials. Does nothing if session has no S3 info yet.
  Future<S3Credentials> refreshS3Credentials() async {
    final res = await _dio.post('/api/refresh-s3-credentials/');
    final creds = S3Credentials.fromJson(res.data as Map<String, dynamic>);
    final current = Session.instance.s3;
    if (current != null) {
      Session.instance.s3 = S3Info(basePath: current.basePath, credentials: creds);
      await Session.instance.persist();
    }
    return creds;
  }

  /// If S3 credentials will expire within [within], refresh them.
  /// Returns the (possibly refreshed) credentials, or null if no S3 session yet.
  Future<S3Credentials?> refreshS3CredentialsIfExpiring({
    Duration within = const Duration(minutes: 5),
  }) async {
    final s3 = Session.instance.s3;
    if (s3 == null) return null;
    final expStr = s3.credentials.expiration;
    DateTime? exp;
    try {
      exp = DateTime.parse(expStr).toUtc();
    } catch (_) {
      exp = null;
    }
    if (exp == null) {
      // If unknown format, be safe and refresh.
      return await refreshS3Credentials();
    }
    final now = DateTime.now().toUtc();
    if (exp.isBefore(now.add(within))) {
      return await refreshS3Credentials();
    }
    return s3.credentials;
  }

  /// Submit a voting paper result.
  Future<void> submitVotingPaperResult({
    required int index,
    required String partyId,
  }) async {
    await _dio.post(
      '/api/votingpaperresult/',
      data: {'index': index, 'party_id': partyId},
    );
  }
}
