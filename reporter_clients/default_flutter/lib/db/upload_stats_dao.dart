import 'package:sembast/sembast.dart';

import 'database.dart';

/// Tracks counters for successfully uploaded images, persisted locally.
class UploadStatsDao {
  UploadStatsDao._();
  static final UploadStatsDao instance = UploadStatsDao._();

  StoreRef<String, Map<String, Object?>> get _store =>
      AppDatabase.instance.uploadStatsStore;
  Database get _db => AppDatabase.instance.db;

  Future<int> getCount(String key) async {
    final rec = await _store.record(key).get(_db);
    if (rec == null) return 0;
    final count = rec['count'];
    if (count is int) return count;
    if (count is num) return count.toInt();
    return 0;
  }

  Future<void> setCount(String key, int count) async {
    await _store.record(key).put(_db, {'count': count});
  }

  Future<int> increment(String key, int delta) async {
    final current = await getCount(key);
    final next = current + delta;
    await setCount(key, next);
    return next;
  }
}

