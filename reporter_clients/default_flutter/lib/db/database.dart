import 'dart:async';
import 'dart:io';

import 'package:path_provider/path_provider.dart';
import 'package:sembast/sembast.dart';
import 'package:sembast/sembast_io.dart';

/// AppDatabase wraps Sembast initialization and provides named stores.
class AppDatabase {
  AppDatabase._();
  static final AppDatabase instance = AppDatabase._();

  late Database _db;
  Database get db => _db;

  /// Store names
  static const String authStoreName = 'auth';
  static const String failedVoteStoreName = 'failed_votes';
  static const String failedVprStoreName = 'failed_vpr';
  static const String candidatePartiesStoreName = 'candidate_parties';
  static const String uploadStatsStoreName = 'upload_stats';
  static const String prefsStoreName = 'prefs';

  final StoreRef<String, Map<String, Object?>> authStore =
      stringMapStoreFactory.store(authStoreName);
  final StoreRef<int, Map<String, Object?>> failedVoteStore =
      intMapStoreFactory.store(failedVoteStoreName);
  final StoreRef<int, Map<String, Object?>> failedVprStore =
      intMapStoreFactory.store(failedVprStoreName);
  final StoreRef<String, Map<String, Object?>> candidatePartiesStore =
      stringMapStoreFactory.store(candidatePartiesStoreName);
  final StoreRef<String, Map<String, Object?>> uploadStatsStore =
      stringMapStoreFactory.store(uploadStatsStoreName);
  final StoreRef<String, Map<String, Object?>> prefsStore =
      stringMapStoreFactory.store(prefsStoreName);

  /// Initialize the local database file.
  Future<void> init() async {
    final Directory dir = await getApplicationDocumentsDirectory();
    final dbPath = '${dir.path}/ufrecs.db';
    _db = await databaseFactoryIo.openDatabase(dbPath);
  }

  /// Wipe the on-disk database and reopen a fresh one.
  /// Safely closes any existing handle, deletes the file, then re-opens it.
  Future<void> wipe() async {
    try {
      await _db.close();
    } catch (_) {
      // Ignore if already closed or not yet opened.
    }
    final Directory dir = await getApplicationDocumentsDirectory();
    final dbPath = '${dir.path}/ufrecs.db';
    try {
      await databaseFactoryIo.deleteDatabase(dbPath);
    } catch (_) {
      // Ignore errors during deletion; we will attempt to open a fresh DB anyway.
    }
    _db = await databaseFactoryIo.openDatabase(dbPath);
  }
}
