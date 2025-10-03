import 'package:sembast/sembast.dart';

import '../models/results.dart';
import 'database.dart';

/// DAO for persisting and reading CandidateParty entries in Sembast.
class CandidatePartyDao {
  CandidatePartyDao._();
  static final CandidatePartyDao instance = CandidatePartyDao._();

  StoreRef<String, Map<String, Object?>> get _store =>
      AppDatabase.instance.candidatePartiesStore;

  Database get _db => AppDatabase.instance.db;

  /// Replace all candidate parties with the given list in a transaction.
  Future<void> replaceAll(List<CandidateParty> items) async {
    await _db.transaction((txn) async {
      // Clear existing
      await _store.delete(txn);
      // Batch insert by identifier as the key
      for (final c in items) {
        await _store.record(c.identifier).put(txn, {
          'id': c.id,
          'party_name': c.partyName,
          'candidate_name': c.candidateName,
          'identifier': c.identifier,
          'created_at': c.createdAt,
        });
      }
    });
  }

  /// Get all candidate parties sorted by candidate_name then party_name.
  Future<List<CandidateParty>> getAll() async {
    final records = await _store.find(_db);
    final list = records
        .map((rec) => CandidateParty(
              id: (rec.value['id'] as num?)?.toInt() ?? 0,
              partyName: rec.value['party_name'] as String? ?? '',
              candidateName: rec.value['candidate_name'] as String? ?? '',
              identifier: rec.value['identifier'] as String? ?? rec.key,
              createdAt: rec.value['created_at'] as String? ?? '',
            ))
        .toList();
    list.sort((a, b) {
      final byCand = a.candidateName.compareTo(b.candidateName);
      if (byCand != 0) return byCand;
      return a.partyName.compareTo(b.partyName);
    });
    return list;
  }
}

