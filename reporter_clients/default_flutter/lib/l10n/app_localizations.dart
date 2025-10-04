import 'package:flutter/widgets.dart';

class AppLocalizations {
  final Locale locale;
  AppLocalizations(this.locale);

  static const supportedLocales = [Locale('en'), Locale('fr')];

  static AppLocalizations of(BuildContext context) =>
      Localizations.of<AppLocalizations>(context, AppLocalizations)!;

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocDelegate();

  static final Map<String, Map<String, String>> _strings = {
    'en': {
      'appTitle': 'UFRECS Reporter',
      'home.votes': 'Votes Session',
      'home.results': 'Results Session',
      'home.home': 'Home',
      'home.list': 'Poll Office List',
      'home.minutes': 'Poll Office Minutes',
      'home.settings': 'Settings',

      'login.electorId': 'Elector ID',
      'login.pollOffice': 'Poll Office',
      'login.searchHint': 'Type 3+ characters to search',
      'login.passwordOptional': 'Password (optional)',
      'login.signIn': 'Sign In',
      'login.authFailed': 'Authentication failed',

      'common.submit': 'Submit',
      'common.cancel': 'Cancel',
      'common.confirm': 'Confirm',
      'common.settings': 'Settings',
      'common.yes': 'Yes',
      'common.no': 'No',

      'upload.noImages': 'No images selected.',
      'upload.missingCreds': 'Missing S3 credentials.',
      'upload.success': 'Uploaded successfully',
      'upload.error': 'Upload failed',
      'upload.failedCount': 'Upload failed for {failed} of {total} file(s).',
      'upload.alreadySent': 'Already sent: {count} image(s)',

      'votes.title': 'Votes Session',
      'votes.nextIndex': 'Next Vote index: {index}',
      'votes.confirmTitle': 'Confirm submission',
      'votes.index': 'Index',
      'votes.gender': 'Gender',
      'votes.age': 'Age',
      'votes.torn': 'Has torn voting paper',
      'votes.male': 'Male',
      'votes.female': 'Female',
      'votes.age1': 'Less than 30',
      'votes.age2': '30 to 60',
      'votes.age3': 'More than 60',

      'results.title': 'Results Session',
      'results.nextIndex': 'Next Voting Paper Result index: {index}',
      'results.confirmChoice': 'Confirm choice',
      'results.paper': 'Paper',

      'settings.title': 'Settings',
      'settings.electorId': 'Elector ID',
      'settings.pollOfficeId': 'Poll Office ID',
      'settings.failedVotes': 'Failed votes',
      'settings.failedVpr': 'Failed voting paper results',
      'settings.resend': 'Resend',
      'settings.contactEmail': 'Contact email',
      'settings.phone1': 'Phone number 1',
      'settings.phone2': 'Phone number 2',
      'settings.devTeam': 'Developer Team',
      'settings.devWebsite': 'Developer Website',
      'settings.logoutAll': 'Logout and Clear All Data',
      'settings.logout': 'Logout',
      'settings.confirmLogout': 'Confirm Logout',
      'settings.logoutMessage':
          'This will clear all local data (tokens, S3 credentials, and database).\nDo you want to continue?',
      'settings.language': 'Language',
      'settings.english': 'English',
      'settings.french': 'French',

      'list.title': 'Poll Office List',
      'minutes.title': 'Poll Office Minutes',
      'form.photos': 'Photos',
    },
    'fr': {
      'appTitle': 'UFRECS Reporter',
      'home.votes': 'Session de votes',
      'home.results': 'Session des résultats',
      'home.home': 'Accueil',
      'home.list': 'Liste du bureau de vote',
      'home.minutes': 'Procès-verbal du bureau de vote',
      'home.settings': 'Paramètres',

      'login.electorId': "ID de l'électeur",
      'login.pollOffice': 'Bureau de vote',
      'login.searchHint': 'Tapez au moins 3 caractères',
      'login.passwordOptional': 'Mot de passe (optionnel)',
      'login.signIn': 'Se connecter',
      'login.authFailed': 'Échec de l’authentification',

      'common.submit': 'Envoyer',
      'common.cancel': 'Annuler',
      'common.confirm': 'Confirmer',
      'common.settings': 'Paramètres',
      'common.yes': 'Oui',
      'common.no': 'Non',

      'upload.noImages': 'Aucune image sélectionnée.',
      'upload.missingCreds': 'Identifiants S3 manquants.',
      'upload.success': 'Téléchargement réussi',
      'upload.error': 'Échec du téléchargement',
      'upload.failedCount': 'Échec pour {failed} sur {total} fichier(s).',
      'upload.alreadySent': 'Déjà envoyées : {count} image(s)',

      'votes.title': 'Session de votes',
      'votes.nextIndex': 'Index du prochain vote : {index}',
      'votes.confirmTitle': 'Confirmer l’envoi',
      'votes.index': 'Index',
      'votes.gender': 'Genre',
      'votes.age': 'Âge',
      'votes.torn': 'Bulletin déchiré',
      'votes.male': 'Homme',
      'votes.female': 'Femme',
      'votes.age1': 'Moins de 30',
      'votes.age2': '30 à 60',
      'votes.age3': 'Plus de 60',

      'results.title': 'Session des résultats',
      'results.nextIndex': 'Index du prochain résultat de bulletin : {index}',
      'results.confirmChoice': 'Confirmer le choix',
      'results.paper': 'Bulletin',

      'settings.title': 'Paramètres',
      'settings.electorId': "ID de l'électeur",
      'settings.pollOfficeId': 'ID du bureau de vote',
      'settings.failedVotes': 'Votes échoués',
      'settings.failedVpr': 'Résultats de bulletins échoués',
      'settings.resend': 'Renvoyer',
      'settings.contactEmail': 'Email de contact',
      'settings.phone1': 'Numéro de téléphone 1',
      'settings.phone2': 'Numéro de téléphone 2',
      'settings.devTeam': 'Équipe de développement',
      'settings.devWebsite': 'Site du développeur',
      'settings.logoutAll': 'Déconnexion et suppression des données',
      'settings.logout': 'Déconnexion',
      'settings.confirmLogout': 'Confirmer la déconnexion',
      'settings.logoutMessage':
          'Cela effacera toutes les données locales (jetons, identifiants S3 et base de données).\nVoulez-vous continuer ?',
      'settings.language': 'Langue',
      'settings.english': 'Anglais',
      'settings.french': 'Français',

      'list.title': 'Liste du bureau de vote',
      'minutes.title': 'Procès-verbal du bureau de vote',
      'form.photos': 'Photos',
    },
  };

  String _tr(String key) {
    final lang = locale.languageCode;
    return _strings[lang]?[key] ?? _strings['en']![key] ?? key;
  }

  String get appTitle => _tr('appTitle');
  String get settings => _tr('common.settings');
  String get submit => _tr('common.submit');
  String get cancel => _tr('common.cancel');
  String get confirm => _tr('common.confirm');
  String get yes => _tr('common.yes');
  String get no => _tr('common.no');

  // Expose specific getters used in pages
  String get homeVotes => _tr('home.votes');
  String get homeResults => _tr('home.results');
  String get homeHome => _tr('home.home');
  String get homeList => _tr('home.list');
  String get homeMinutes => _tr('home.minutes');
  String get homeSettings => _tr('home.settings');

  String uploadedFailedCount(int failed, int total) => _tr(
    'upload.failedCount',
  ).replaceFirst('{failed}', '$failed').replaceFirst('{total}', '$total');
  String alreadySentCount(int count) =>
      _tr('upload.alreadySent').replaceFirst('{count}', '$count');

  String get uploadNoImages => _tr('upload.noImages');
  String get uploadMissingCreds => _tr('upload.missingCreds');
  String get uploadSuccess => _tr('upload.success');
  String get uploadError => _tr('upload.error');

  String get listTitle => _tr('list.title');
  String get minutesTitle => _tr('minutes.title');
  String get formPhotos => _tr('form.photos');

  String get votesTitle => _tr('votes.title');
  String votesNextIndex(int index) =>
      _tr('votes.nextIndex').replaceFirst('{index}', '$index');
  String get votesConfirmTitle => _tr('votes.confirmTitle');
  String get votesIndex => _tr('votes.index');
  String get votesGender => _tr('votes.gender');
  String get votesAge => _tr('votes.age');
  String get votesTorn => _tr('votes.torn');
  String get votesMale => _tr('votes.male');
  String get votesFemale => _tr('votes.female');
  String get votesAge1 => _tr('votes.age1');
  String get votesAge2 => _tr('votes.age2');
  String get votesAge3 => _tr('votes.age3');

  String get resultsTitle => _tr('results.title');
  String resultsNextIndex(int index) =>
      _tr('results.nextIndex').replaceFirst('{index}', '$index');
  String get resultsConfirmChoice => _tr('results.confirmChoice');
  String get resultsPaper => _tr('results.paper');

  String get loginElectorId => _tr('login.electorId');
  String get loginPollOffice => _tr('login.pollOffice');
  String get loginSearchHint => _tr('login.searchHint');
  String get loginPasswordOptional => _tr('login.passwordOptional');
  String get loginSignIn => _tr('login.signIn');
  String get loginAuthFailed => _tr('login.authFailed');
  String get loginApiPrefix => _tr('login.apiPrefix');

  String get settingsTitle => _tr('settings.title');
  String get settingsElectorId => _tr('settings.electorId');
  String get settingsPollOfficeId => _tr('settings.pollOfficeId');
  String get settingsFailedVotes => _tr('settings.failedVotes');
  String get settingsFailedVpr => _tr('settings.failedVpr');
  String get settingsResend => _tr('settings.resend');
  String get settingsContactEmail => _tr('settings.contactEmail');
  String get settingsPhone1 => _tr('settings.phone1');
  String get settingsPhone2 => _tr('settings.phone2');
  String get settingsDevTeam => _tr('settings.devTeam');
  String get settingsDevWebsite => _tr('settings.devWebsite');
  String get settingsLogoutAll => _tr('settings.logoutAll');
  String get settingsLogout => _tr('settings.logout');
  String get settingsConfirmLogout => _tr('settings.confirmLogout');
  String get settingsLogoutMessage => _tr('settings.logoutMessage');
  String get settingsLanguage => _tr('settings.language');
  String get settingsEnglish => _tr('settings.english');
  String get settingsFrench => _tr('settings.french');
}

class _AppLocDelegate extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocDelegate();
  @override
  bool isSupported(Locale locale) => ['en', 'fr'].contains(locale.languageCode);

  @override
  Future<AppLocalizations> load(Locale locale) async =>
      AppLocalizations(locale);

  @override
  bool shouldReload(_AppLocDelegate old) => false;
}

extension AppLocalizationsX on BuildContext {
  AppLocalizations get l10n => AppLocalizations.of(this);
}
