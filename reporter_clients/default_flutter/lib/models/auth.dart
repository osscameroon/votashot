/// Authentication response and S3 credentials models.
class AuthenticateResponse {
  final String token;
  final String pollOfficeId;
  final S3Info s3;

  AuthenticateResponse({
    required this.token,
    required this.pollOfficeId,
    required this.s3,
  });

  factory AuthenticateResponse.fromJson(Map<String, dynamic> json) {
    return AuthenticateResponse(
      token: json['token'] as String,
      pollOfficeId: json['poll_office_id'] as String,
      s3: S3Info.fromJson(json['s3'] as Map<String, dynamic>),
    );
  }

  Map<String, dynamic> toJson() => {
        'token': token,
        'poll_office_id': pollOfficeId,
        's3': s3.toJson(),
      };
}

class S3Info {
  final String basePath;
  final S3Credentials credentials;

  S3Info({required this.basePath, required this.credentials});

  factory S3Info.fromJson(Map<String, dynamic> json) => S3Info(
        basePath: json['base_path'] as String,
        credentials: S3Credentials.fromJson(
            json['credentials'] as Map<String, dynamic>),
      );

  Map<String, dynamic> toJson() => {
        'base_path': basePath,
        'credentials': credentials.toJson(),
      };
}

class S3Credentials {
  final String bucket;
  final String region;
  final String endpoint;
  final String prefix;
  final String accessKeyId;
  final String secretAccessKey;
  final String sessionToken;
  final String expiration;

  S3Credentials({
    required this.bucket,
    required this.region,
    required this.endpoint,
    required this.prefix,
    required this.accessKeyId,
    required this.secretAccessKey,
    required this.sessionToken,
    required this.expiration,
  });

  factory S3Credentials.fromJson(Map<String, dynamic> json) {
    final region = json['region'] as String;
    final endpoint = (json['endpoint'] as String?) ??
        'https://s3.$region.wasabisys.com'; // backward-compat default
    return S3Credentials(
      bucket: json['bucket'] as String,
      region: region,
      endpoint: endpoint,
      prefix: json['prefix'] as String,
      accessKeyId: json['accessKeyId'] as String,
      secretAccessKey: json['secretAccessKey'] as String,
      sessionToken: json['sessionToken'] as String,
      expiration: json['expiration'] as String,
    );
  }

  Map<String, dynamic> toJson() => {
        'bucket': bucket,
        'region': region,
        'endpoint': endpoint,
        'prefix': prefix,
        'accessKeyId': accessKeyId,
        'secretAccessKey': secretAccessKey,
        'sessionToken': sessionToken,
        'expiration': expiration,
      };
}
