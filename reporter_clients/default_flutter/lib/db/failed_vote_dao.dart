import 'package:sembast/sembast.dart';

import '../models/vote.dart';
import '../services/api_client.dart';
import 'database.dart';

/// DAO for persisting and resubmitting failed vote submissions.
class FailedVoteDao {
  FailedVoteDao._();
  static final FailedVoteDao instance = FailedVoteDao._();

  final StoreRef<int, Map<String, Object?>> _store =
      AppDatabase.instance.failedVoteStore;

  Future<void> add(VotePayload payload) async {
    await _store.add(AppDatabase.instance.db, payload.toJson());
  }

  Future<int> count() async {
    final finder = Finder();
    return _store.count(AppDatabase.instance.db);
  }

  Future<int> resendAll() async {
    final db = AppDatabase.instance.db;
    final records = await _store.find(db);
    int success = 0;
    for (final rec in records) {
      final data = rec.value;
      try {
        await ApiClient.instance.submitVote(
          VotePayload(
            index: (data['index'] as num).toInt(),
            gender: data['gender'] as String,
            age: data['age'] as String,
            hasTorn: data['has_torn'] as bool,
          ),
        );
        await _store.record(rec.key).delete(db);
        success++;
      } catch (_) {
        // Keep in DB on failure.
      }
    }
    return success;
  }
}
