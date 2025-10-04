import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_form_builder/flutter_form_builder.dart';
import 'package:form_builder_extra_fields/form_builder_extra_fields.dart';
import 'package:form_builder_validators/form_builder_validators.dart';

import '../config/app_config.dart';
import '../db/candidate_party_dao.dart';
import '../l10n/app_localizations.dart';
import '../models/poll_office.dart';
import '../services/api_client.dart';
import '../state/session.dart';

/// Authentication page using flutter_form_builder.
class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormBuilderState>();
  Timer? _debounce;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    // If a session is already persisted, immediately redirect to Home.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      if (Session.instance.isAuthenticated) {
        Navigator.of(context).pushReplacementNamed(AppRouter.homeRoute);
      }
    });
  }

  @override
  void dispose() {
    _debounce?.cancel();
    super.dispose();
  }

  Future<void> _submit() async {
    final state = _formKey.currentState!;
    if (!state.saveAndValidate()) return;
    setState(() => _loading = true);
    try {
      final electorId = state.value['elector_id'] as String;
      final password = state.value['password'] as String?;
      final pollOfficeId = state.value['poll_office_id'] as String;
      await ApiClient.instance.authenticate(
        electorId: electorId,
        pollOfficeId: pollOfficeId,
        password: password,
      );
      // After successful authentication, fetch and cache candidate parties.
      try {
        final candidates = await ApiClient.instance.getCandidateParties();
        await CandidatePartyDao.instance.replaceAll(candidates);
      } catch (error, stacktrace) {
        debugPrint(error.toString());
        debugPrintStack(stackTrace: stacktrace);
      }
      if (!mounted) return;
      Navigator.of(context).pushReplacementNamed(AppRouter.homeRoute);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('${context.l10n.loginAuthFailed}: $e')),
      );
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // No AppBar per requirements.
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 24),
              Text(
                context.l10n.appTitle,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              Expanded(
                child: SingleChildScrollView(
                  child: FormBuilder(
                    key: _formKey,
                    child: Column(
                      children: [
                        FormBuilderTextField(
                          name: 'elector_id',
                          decoration: InputDecoration(
                            labelText: context.l10n.loginElectorId,
                            border: const OutlineInputBorder(),
                          ),
                          validator: FormBuilderValidators.compose([
                            FormBuilderValidators.required(),
                          ]),
                        ),
                        const SizedBox(height: 16),
                        // Searchable dropdown for poll office using async fetch
                        FormBuilderSearchableDropdown<PollOffice>(
                          name: 'poll_office_id',
                          decoration: InputDecoration(
                            labelText: context.l10n.loginPollOffice,
                            hintText: context.l10n.loginSearchHint,
                            border: const OutlineInputBorder(),
                          ),
                          asyncItems: (String filter, LoadProps? props) async {
                            final q = (filter ?? '').trim();
                            if (q.length < 3) return [];
                            try {
                              return await ApiClient.instance.searchPollOffices(
                                q,
                              );
                            } catch (_) {
                              return [];
                            }
                          },
                          compareFn: (a, b) => a.identifier == b.identifier,
                          popupProps: const PopupProps.menu(
                            showSearchBox: true,
                          ),
                          itemAsString: (po) => '${po.name} (${po.identifier})',
                          // Store identifier as value in form state
                          valueTransformer: (po) => po?.identifier,
                          validator: FormBuilderValidators.required(),
                        ),
                        const SizedBox(height: 16),
                        FormBuilderTextField(
                          name: 'password',
                          obscureText: true,
                          decoration: InputDecoration(
                            labelText: context.l10n.loginPasswordOptional,
                            border: const OutlineInputBorder(),
                          ),
                        ),
                        const SizedBox(height: 24),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            onPressed: _loading ? null : _submit,
                            icon: _loading
                                ? const SizedBox(
                                    height: 18,
                                    width: 18,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                    ),
                                  )
                                : const Icon(Icons.login),
                            label: Text(context.l10n.loginSignIn),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Text(
                '${context.l10n.loginApiPrefix} ${AppConfig.apiBaseUrl}',
                textAlign: TextAlign.center,
                style: Theme.of(
                  context,
                ).textTheme.labelSmall?.copyWith(color: Colors.grey),
              ),
              const SizedBox(height: 8),
            ],
          ),
        ),
      ),
    );
  }
}
