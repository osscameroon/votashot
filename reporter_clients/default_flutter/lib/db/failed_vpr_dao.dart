import 'package:sembast/sembast.dart';

import '../services/api_client.dart';
import 'database.dart';

/// DAO for persisting and resubmitting failed voting paper results.
class FailedVotingPaperResultDao {
  FailedVotingPaperResultDao._();
  static final FailedVotingPaperResultDao instance =
      FailedVotingPaperResultDao._();

  final StoreRef<int, Map<String, Object?>> _store =
      AppDatabase.instance.failedVprStore;

  Future<void> add({required int index, required String partyId}) async {
    await _store.add(AppDatabase.instance.db, {
      'index': index,
      'party_id': partyId,
    });
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
        await ApiClient.instance.submitVotingPaperResult(
          index: (data['index'] as num).toInt(),
          partyId: data['party_id'] as String,
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
