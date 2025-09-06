import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ufrecscitizen/services/api_client.dart';

class _MockAdapter implements HttpClientAdapter {
  int calls = 0;

  @override
  void close({bool force = false}) {}

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<List<int>>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    calls += 1;

    // Only handle the polloffices endpoint in this mock
    if (options.path != '/api/polloffices/') {
      return ResponseBody.fromString(
        jsonEncode({'detail': 'Not Found'}),
        404,
        headers: {
          Headers.contentTypeHeader: [Headers.jsonContentType],
        },
      );
    }

    final limit = int.parse('${options.queryParameters['limit'] ?? '0'}');
    final offset = int.parse('${options.queryParameters['offset'] ?? '0'}');

    Map<String, dynamic> page(int offset) {
      if (offset == 0) {
        return {
          'count': 3,
          'next': 'http://test/api/polloffices/?limit=$limit&offset=2',
          'previous': null,
          'results': [
            {'id': 1, 'name': 'Office A'},
            {'id': 2, 'name': 'Office B'},
          ],
        };
      }
      return {
        'count': 3,
        'next': null,
        'previous': 'http://test/api/polloffices/?limit=$limit',
        'results': [
          {'id': 3, 'name': 'Office C'},
        ],
      };
    }

    final body = page(offset);
    return ResponseBody.fromString(
      jsonEncode(body),
      200,
      headers: {
        Headers.contentTypeHeader: [Headers.jsonContentType],
      },
    );
  }
}

void main() {
  test('getPollOffices paginates and caches', () async {
    final dio = Dio(BaseOptions(baseUrl: 'http://test'));
    final adapter = _MockAdapter();
    dio.httpClientAdapter = adapter;

    final api = ApiClient.withDio(dio);

    // First call paginates across two pages
    final first = await api.getPollOffices();
    expect(first.map((e) => e.id).toList(), [1, 2, 3]);
    expect(adapter.calls, 2); // two pages fetched

    // Second call should reuse cache, no new HTTP calls
    final second = await api.getPollOffices();
    expect(identical(first, second), isTrue); // returns cached list instance
    expect(adapter.calls, 2); // still 2, no extra fetch
  });
}

