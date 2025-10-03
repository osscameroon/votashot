import 'package:aws_common/aws_common.dart';
import 'package:aws_signature_v4/aws_signature_v4.dart';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../models/auth.dart';

/// Result info from an S3-compatible PUT upload.
class S3PutResult {
  final int statusCode;
  final String requestUrl;
  final String? eTag; // ETag header if present
  final String? versionId; // x-amz-version-id if present
  S3PutResult({
    required this.statusCode,
    required this.requestUrl,
    this.eTag,
    this.versionId,
  });
}

/// Joins "folder" + "file.jpg" => "folder/file.jpg" (no double slashes).
String _joinKey(String? prefix, String objectKey) {
  final a = (prefix ?? '').trim();
  final b = objectKey.trim();
  if (a.isEmpty) return b;
  return [
    a.replaceAll(RegExp(r'^/+|/+$'), ''),
    b.replaceAll(RegExp(r'^/+'), ''),
  ].where((s) => s.isNotEmpty).join('/');
}

/// Minimal AWS SigV4 signer and uploader for S3 PUT Object.
/// Uses temporary credentials from backend (STS) contained in [S3Info].
class S3Uploader {
  /// Upload bytes to any S3-compatible storage using SigV4.
  /// - Works with AWS, DigitalOcean Spaces, Wasabi, Backblaze B2 S3, MinIO, etc.
  /// - Supports virtual-hosted *and* path-style URLs.
  /// - Allows targeting a specific folder/prefix via [keyPrefix].
  ///
  /// [endpoint] examples:
  ///   AWS:        "https://s3.us-east-1.amazonaws.com"
  ///               (with virtualHost=true -> bucket.s3.us-east-1.amazonaws.com)
  ///   DO Spaces:  "https://nyc3.digitaloceanspaces.com"
  ///   Wasabi:     "https://s3.us-east-1.wasabisys.com"
  ///   Backblaze:  "https://s3.us-west-000.backblazeb2.com"
  ///   MinIO:      "http://minio.yourcompany.com:9000"
  ///
  /// [region] is required for SigV4. Many S3-compatible providers accept "us-east-1".
  /// [virtualHost] = true => https://{bucket}.{endpointHost}/{key}
  /// [virtualHost] = false => https://{endpointHost}/{bucket}/{key}
  ///
  /// Provide [sessionToken] only if you’re using AWS STS. It’s optional for most 3rd-party providers.
  ///
  /// Returns [S3PutResult] with status code, ETag, etc.
  Future<S3PutResult> putToS3({
    // Endpoint & routing
    required String
    endpoint, // may include scheme + port (e.g., "https://nyc3.digitaloceanspaces.com")
    required String
    region, // e.g., "us-east-1" (common default for non-AWS providers)
    required String bucket,
    required String
    objectKey, // file name or relative key (e.g., "photo.jpg" or "user42/photo.jpg")
    String? keyPrefix, // optional folder/prefix (e.g., "users/42/uploads")
    bool virtualHost =
        true, // set false for providers that require path-style (MinIO often OK either way)
    // Data
    required List<int> bytes,
    String contentType = 'application/octet-stream',
    // Credentials
    required String accessKeyId,
    required String secretAccessKey,
    String? sessionToken, // only for STS; omit for static creds
    // Extras
    Map<String, String>?
    extraHeaders, // e.g., {'x-amz-acl': 'private', 'x-amz-meta-origin': 'mobile'}
    String serviceName =
        's3', // override only if your provider requires a different SigV4 service name
  }) async {
    if (kDebugMode) {
      debugPrint('[S3Uploader.putToS3] called with');
      debugPrint('  endpoint=$endpoint');
      debugPrint('  region=$region bucket=$bucket');
      debugPrint('  objectKey=$objectKey keyPrefix=${keyPrefix ?? ''}');
      debugPrint('  virtualHost=$virtualHost');
      debugPrint('  bytes.length=${bytes.length} contentType=$contentType');
      debugPrint('  accessKeyId=${accessKeyId}');
      debugPrint('  secretAccessKey=${secretAccessKey}');
      if (sessionToken != null && sessionToken.isNotEmpty) {
        debugPrint('  sessionToken=${sessionToken}');
      }
      debugPrint('  extraHeaders=${extraHeaders?.keys.toList() ?? []}');
      debugPrint('  serviceName=$serviceName');
    }
    // Normalize/parse endpoint (scheme/host/port)
    final epUri = endpoint.contains('://')
        ? Uri.parse(endpoint)
        : Uri.parse('https://$endpoint');

    final scheme = epUri.scheme.isEmpty ? 'https' : epUri.scheme;
    final hostBase = epUri.host;
    final port = epUri.hasPort ? epUri.port : null;

    // Build the final key with optional prefix
    final key = _joinKey(keyPrefix, objectKey);

    // Choose host & path based on addressing style
    final host = virtualHost ? '$bucket.$hostBase' : hostBase;
    final path = virtualHost ? '/$key' : '/$bucket/$key';

    final uri = Uri(
      scheme: scheme,
      host: host,
      port: port == 0 ? null : port,
      path: path,
    );

    // Prepare credentials & signer
    final creds = AWSCredentials(accessKeyId, secretAccessKey, sessionToken);
    final signer = AWSSigV4Signer(
      credentialsProvider: AWSCredentialsProvider(creds),
    );

    // Base headers
    final headers = <String, String>{
      'host': host,
      'content-type': contentType,
      if (sessionToken != null && sessionToken.isNotEmpty)
        'x-amz-security-token': sessionToken,
      // Add any default hardening headers if your bucket policy requires them:
      // 'x-amz-server-side-encryption': 'AES256',
      // 'x-amz-acl': 'private',
      ...?extraHeaders,
    };

    // Build the signed request
    final signed = await signer.sign(
      AWSHttpRequest(
        method: AWSHttpMethod.put,
        uri: uri,
        headers: headers,
        body: bytes,
      ),
      credentialScope: AWSCredentialScope(
        region: region,
        service: AWSService(serviceName), // usually 's3'
      ),
    );

    if (kDebugMode) {
      debugPrint('[S3Uploader.putToS3] PUT ${uri.toString()}');
    }

    // Execute the HTTP request with Dio (keeps signed headers intact)
    final dio = Dio(
      BaseOptions(followRedirects: false, validateStatus: (_) => true),
    );

    final response = await dio.putUri(
      uri,
      data: bytes,
      options: Options(
        headers: signed.headers,
        responseType: ResponseType.bytes,
        contentType: contentType,
      ),
    );

    if (kDebugMode) {
      debugPrint('[S3Uploader.putToS3] status=${response.statusCode}');
    }

    return S3PutResult(
      statusCode: response.statusCode ?? 0,
      requestUrl: uri.toString(),
      eTag: response.headers.value('etag') ?? response.headers.value('ETag'),
      versionId:
          response.headers.value('x-amz-version-id') ??
          response.headers.value('X-Amz-Version-Id'),
    );
  }

  /// Backward-compatible convenience wrapper for AWS STS:
  /// Keeps your old name but now just delegates to [putToS3].
  Future<S3PutResult> putWithSTS({
    required String bucket,
    required String region,
    required String key, // full path within the bucket
    required List<int> bytes,
    required String contentType,
    required String accessKeyId,
    required String secretAccessKey,
    required String sessionToken,
    Map<String, String>? extraHeaders,
  }) {
    return putToS3(
      endpoint: 'https://s3.$region.amazonaws.com',
      region: region,
      bucket: bucket,
      objectKey: key,
      bytes: bytes,
      contentType: contentType,
      accessKeyId: accessKeyId,
      secretAccessKey: secretAccessKey,
      sessionToken: sessionToken,
      virtualHost: true,
      extraHeaders: extraHeaders,
    );
  }
}

String _redact(String value, {int showFirst = 0, int showLast = 0}) {
  if (value.isEmpty) return value;
  final keepStart = showFirst.clamp(0, value.length);
  final keepEnd = showLast.clamp(0, value.length - keepStart);
  final start = value.substring(0, keepStart);
  final end = value.substring(value.length - keepEnd);
  final hidden = value.length - keepStart - keepEnd;
  return '$start${'*' * (hidden > 0 ? hidden : 0)}$end';
}
