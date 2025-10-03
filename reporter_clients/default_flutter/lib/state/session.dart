import 'dart:convert';

import 'package:sembast/sembast.dart';

import '../db/database.dart';
import '../models/auth.dart';

/// Session holds authenticated state and persists it to local DB.
class Session {
  Session._();
  static final Session instance = Session._();

  String? token;
  String? electorId;
  String? pollOfficeId;
  S3Info? s3;

  bool get isAuthenticated => token != null && token!.isNotEmpty;

  /// Restore previously persisted session from Sembast.
  Future<void> restore() async {
    final db = AppDatabase.instance.db;
    final record = await AppDatabase.instance.authStore
        .record('session')
        .get(db);
    if (record != null) {
      token = record['token'] as String?;
      electorId = record['elector_id'] as String?;
      pollOfficeId = record['poll_office_id'] as String?;
      final s3Json = record['s3'] as String?;
      if (s3Json != null) {
        s3 = S3Info.fromJson(jsonDecode(s3Json) as Map<String, dynamic>);
      }
    }
  }

  /// Persist the session to local DB for later restarts.
  Future<void> persist() async {
    final db = AppDatabase.instance.db;
    await AppDatabase.instance.authStore.record('session').put(db, {
      'token': token ?? '',
      'elector_id': electorId ?? '',
      'poll_office_id': pollOfficeId ?? '',
      's3': s3 == null ? null : jsonEncode(s3!.toJson()),
    });
  }

  /// Clear the session data.
  Future<void> clear() async {
    token = null;
    electorId = null;
    pollOfficeId = null;
    s3 = null;
    final db = AppDatabase.instance.db;
    await AppDatabase.instance.authStore.record('session').delete(db);
  }
}
