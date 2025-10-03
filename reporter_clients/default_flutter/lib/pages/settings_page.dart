import 'package:flutter/material.dart';

import '../config/app_config.dart';
import '../db/database.dart';
import '../db/failed_vote_dao.dart';
import '../db/failed_vpr_dao.dart';
import '../l10n/app_localizations.dart';
import '../state/locale_controller.dart';
import '../state/session.dart';
import '../widgets/app_bottom_nav.dart';

/// Settings page showing session and resync controls.
class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  int _failedVotes = 0;
  int _failedVpr = 0;
  bool _resyncingVotes = false;
  bool _resyncingVpr = false;

  @override
  void initState() {
    super.initState();
    _refreshCounts();
  }

  Future<void> _refreshCounts() async {
    final v = await FailedVoteDao.instance.count();
    final r = await FailedVotingPaperResultDao.instance.count();
    if (!mounted) return;
    setState(() {
      _failedVotes = v;
      _failedVpr = r;
    });
  }

  Future<void> _resendVotes() async {
    setState(() => _resyncingVotes = true);
    await FailedVoteDao.instance.resendAll();
    if (mounted) setState(() => _resyncingVotes = false);
    await _refreshCounts();
  }

  Future<void> _resendVpr() async {
    setState(() => _resyncingVpr = true);
    await FailedVotingPaperResultDao.instance.resendAll();
    if (mounted) setState(() => _resyncingVpr = false);
    await _refreshCounts();
  }

  @override
  Widget build(BuildContext context) {
    final s = Session.instance;
    return Scaffold(
      appBar: AppBar(
        title: Text(context.l10n.settingsTitle),
        automaticallyImplyLeading: false,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          ListTile(
            title: Text(context.l10n.settingsLanguage),
            subtitle: Text(LocaleController.instance.value?.languageCode == 'fr'
                ? context.l10n.settingsFrench
                : context.l10n.settingsEnglish),
            trailing: DropdownButton<String>(
              value: LocaleController.instance.value?.languageCode ?? 'en',
              items: [
                DropdownMenuItem(
                  value: 'en',
                  child: Text(context.l10n.settingsEnglish),
                ),
                DropdownMenuItem(
                  value: 'fr',
                  child: Text(context.l10n.settingsFrench),
                ),
              ],
              onChanged: (v) async {
                if (v == null) return;
                await LocaleController.instance.setLanguageCode(v);
                if (mounted) setState(() {});
              },
            ),
          ),
          const Divider(),
          ListTile(
            title: Text(context.l10n.settingsElectorId),
            subtitle: Text(s.electorId ?? '-'),
          ),
          ListTile(
            title: Text(context.l10n.settingsPollOfficeId),
            subtitle: Text(s.pollOfficeId ?? '-'),
          ),
          const Divider(),
          ListTile(
            title: Text(context.l10n.settingsFailedVotes),
            subtitle: Text('$_failedVotes'),
            trailing: _failedVotes > 0
                ? ElevatedButton(
                    onPressed: _resyncingVotes ? null : _resendVotes,
                    child: _resyncingVotes
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : Text(context.l10n.settingsResend),
                  )
                : null,
          ),
          ListTile(
            title: Text(context.l10n.settingsFailedVpr),
            subtitle: Text('$_failedVpr'),
            trailing: _failedVpr > 0
                ? ElevatedButton(
                    onPressed: _resyncingVpr ? null : _resendVpr,
                    child: _resyncingVpr
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : Text(context.l10n.settingsResend),
                  )
                : null,
          ),
          const Divider(),
          ListTile(
            title: Text(context.l10n.settingsContactEmail),
            subtitle: SelectableText(AppConfig.contactEmail),
          ),
          ListTile(
            title: Text(context.l10n.settingsPhone1),
            subtitle: SelectableText(AppConfig.contactPhone1),
          ),
          ListTile(
            title: Text(context.l10n.settingsPhone2),
            subtitle: SelectableText(AppConfig.contactPhone2),
          ),
          ListTile(
            title: Text(context.l10n.settingsDevTeam),
            subtitle: const Text("OSSCameroon"),
          ),
          ListTile(
            title: Text(context.l10n.settingsDevWebsite),
            subtitle: const SelectableText("https://osscameroon.com"),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            icon: const Icon(Icons.logout),
            label: Text(context.l10n.settingsLogoutAll),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            onPressed: _onLogoutPressed,
          ),
        ],
      ),
      bottomNavigationBar: const AppBottomNav(currentIndex: 3),
    );
  }

  Future<void> _onLogoutPressed() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(context.l10n.settingsConfirmLogout),
        content: Text(
          context.l10n.settingsLogoutMessage,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: Text(context.l10n.cancel),
          ),
          FilledButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            child: Text(context.l10n.settingsLogout),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    // Clear session (tokens + S3 credentials) and wipe database file.
    try {
      await Session.instance.clear();
      await AppDatabase.instance.wipe();
    } catch (_) {
      // Ignore errors; proceed to navigation.
    }

    if (!mounted) return;
    Navigator.of(
      context,
    ).pushNamedAndRemoveUntil(AppRouter.loginRoute, (route) => false);
  }
}
