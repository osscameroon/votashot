import 'package:flutter/material.dart';
import 'package:flutter_form_builder/flutter_form_builder.dart';
import 'package:form_builder_validators/form_builder_validators.dart';

import '../db/failed_vote_dao.dart';
import '../l10n/app_localizations.dart';
import '../models/vote.dart';
import '../services/api_client.dart';
import '../state/session.dart';
import '../widgets/app_bottom_nav.dart';

/// Votes Session page: submit per-vote data and queue on failure.
class VotesSessionPage extends StatefulWidget {
  const VotesSessionPage({super.key});

  @override
  State<VotesSessionPage> createState() => _VotesSessionPageState();
}

class _VotesSessionPageState extends State<VotesSessionPage> {
  final _formKey = GlobalKey<FormBuilderState>();
  int _nextIndex = 1;
  bool _loading = true;
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
      final stats = await ApiClient.instance.getPollOfficeStats(pollOfficeId);
      final last = stats.lastVote;
      setState(
        () =>
            _nextIndex = (last == null || last.index == 0) ? 1 : last.index + 1,
      );
    } catch (error, stacktrace) {
      debugPrintStack(stackTrace: stacktrace);
      setState(() => _nextIndex = 1);
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _send(VotePayload payload) async {
    setState(() => _submitting = true);
    try {
      await ApiClient.instance.submitVote(payload);
    } catch (_) {
      await FailedVoteDao.instance.add(payload);
    } finally {
      setState(() {
        _submitting = false;
        _nextIndex += 1;
      });
      _formKey.currentState?.reset();
    }
  }

  Future<void> _confirmAndSubmit() async {
    final form = _formKey.currentState!;
    if (!form.saveAndValidate()) return;
    final gender = form.value['gender'] as String;
    final age = form.value['age'] as String;
    final hasTorn = (form.value['has_torn'] as bool?) ?? false;
    final payload = VotePayload(
      index: _nextIndex,
      gender: gender,
      age: age,
      hasTorn: hasTorn,
    );

    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(context.l10n.votesConfirmTitle),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('${context.l10n.votesIndex}: ${payload.index}'),
            Text('${context.l10n.votesGender}: ${payload.gender}'),
            Text('${context.l10n.votesAge}: ${payload.age}'),
            Text(
              '${context.l10n.votesTorn}: ${payload.hasTorn ? context.l10n.yes : context.l10n.no}',
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: Text(context.l10n.cancel),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            child: Text(context.l10n.confirm),
          ),
        ],
      ),
    );
    if (ok == true) {
      await _send(payload);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(context.l10n.votesTitle),
        automaticallyImplyLeading: false,
        leading: const SizedBox.shrink(),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    context.l10n.votesNextIndex(_nextIndex),
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  FormBuilder(
                    key: _formKey,
                    child: Column(
                      children: [
                        FormBuilderRadioGroup<String>(
                          name: 'gender',
                          decoration: InputDecoration(
                            labelText: context.l10n.votesGender,
                            border: const OutlineInputBorder(),
                          ),
                          validator: FormBuilderValidators.required(),
                          options: [
                            FormBuilderFieldOption(
                              value: 'male',
                              child: Text(context.l10n.votesMale),
                            ),
                            FormBuilderFieldOption(
                              value: 'female',
                              child: Text(context.l10n.votesFemale),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        FormBuilderRadioGroup<String>(
                          name: 'age',
                          decoration: InputDecoration(
                            labelText: context.l10n.votesAge,
                            border: const OutlineInputBorder(),
                          ),
                          validator: FormBuilderValidators.required(),
                          options: [
                            FormBuilderFieldOption(
                              value: 'less_30',
                              child: Text(context.l10n.votesAge1),
                            ),
                            FormBuilderFieldOption(
                              value: 'less_60',
                              child: Text(context.l10n.votesAge2),
                            ),
                            FormBuilderFieldOption(
                              value: 'more_60',
                              child: Text(context.l10n.votesAge3),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        FormBuilderCheckbox(
                          name: 'has_torn',
                          initialValue: false,
                          title: Text(context.l10n.votesTorn),
                        ),
                        const SizedBox(height: 24),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            onPressed: _submitting ? null : _confirmAndSubmit,
                            icon: _submitting
                                ? const SizedBox(
                                    width: 18,
                                    height: 18,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                    ),
                                  )
                                : const Icon(Icons.send),
                            label: Text(context.l10n.submit),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
      bottomNavigationBar: const AppBottomNav(currentIndex: 1),
    );
  }
}
