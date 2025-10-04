import 'package:flutter/material.dart';

import '../db/candidate_party_dao.dart';
import '../db/failed_vpr_dao.dart';
import '../l10n/app_localizations.dart';
import '../models/results.dart';
import '../services/api_client.dart';
import '../state/session.dart';
import '../widgets/app_bottom_nav.dart';

/// Results Session page: choose candidate per paper and queue on failure.
class ResultsSessionPage extends StatefulWidget {
  const ResultsSessionPage({super.key});

  @override
  State<ResultsSessionPage> createState() => _ResultsSessionPageState();
}

class _ResultsSessionPageState extends State<ResultsSessionPage> {
  bool _loading = true;
  int _nextIndex = 1;
  List<CandidateParty> _candidates = [];
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    setState(() => _loading = true);
    try {
      final pollOfficeId = Session.instance.pollOfficeId ?? '';
      final res = await ApiClient.instance.getPollOfficeResults(pollOfficeId);
      final last = res.lastPaper;
      _nextIndex = (last == null || last.index == 0) ? 1 : last.index + 1;
    } catch (_) {
      _nextIndex = 1;
    }
    try {
      // Load candidates from local Sembast cache populated after login.
      _candidates = await CandidatePartyDao.instance.getAll();
      // Fallback: if empty, fetch from backend once and cache.
      if (_candidates.isEmpty) {
        try {
          final fetched = await ApiClient.instance.getCandidateParties();
          await CandidatePartyDao.instance.replaceAll(fetched);
          _candidates = await CandidatePartyDao.instance.getAll();
        } catch (_) {
          // Keep empty on failure; UI will reflect no candidates.
        }
      }
    } catch (_) {
      _candidates = [];
    }
    if (!mounted) return;
    setState(() => _loading = false);
  }

  Future<void> _choose(CandidateParty c) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(context.l10n.resultsConfirmChoice),
        content: Text(
          '${context.l10n.resultsPaper} $_nextIndex\n${c.candidateName} (${c.partyName})',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text(context.l10n.cancel),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: Text(context.l10n.confirm),
          ),
        ],
      ),
    );
    if (ok != true) return;
    setState(() => _submitting = true);
    try {
      await ApiClient.instance.submitVotingPaperResult(
        index: _nextIndex,
        partyId: c.identifier,
      );
    } catch (_) {
      await FailedVotingPaperResultDao.instance.add(
        index: _nextIndex,
        partyId: c.identifier,
      );
    } finally {
      setState(() {
        _nextIndex += 1;
        _submitting = false;
        // Move selected to front
        _candidates.removeWhere((e) => e.identifier == c.identifier);
        _candidates = [c, ..._candidates];
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final crossAxisCount = MediaQuery.of(context).size.width > 600 ? 3 : 2;
    return Scaffold(
      appBar: AppBar(
        title: Text(context.l10n.resultsTitle),
        automaticallyImplyLeading: false,
        leading: const SizedBox.shrink(),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    context.l10n.resultsNextIndex(_nextIndex),
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Expanded(
                  child: GridView.builder(
                    padding: const EdgeInsets.all(16),
                    gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: crossAxisCount,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: 1.2,
                    ),
                    itemCount: _candidates.length,
                    itemBuilder: (ctx, i) {
                      final c = _candidates[i];
                      return Card(
                        elevation: 2,
                        child: InkWell(
                          onTap: _submitting ? null : () => _choose(c),
                          child: Padding(
                            padding: const EdgeInsets.all(12),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(
                                  c.candidateName,
                                  textAlign: TextAlign.center,
                                  style: Theme.of(context).textTheme.titleMedium
                                      ?.copyWith(fontWeight: FontWeight.bold),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  c.partyName,
                                  textAlign: TextAlign.center,
                                  style: Theme.of(context).textTheme.bodyMedium
                                      ?.copyWith(color: Colors.grey[700]),
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
      bottomNavigationBar: const AppBottomNav(currentIndex: 2),
    );
  }
}
