import 'dart:ui';

import 'package:flutter/foundation.dart';
import 'package:sembast/sembast.dart';

import '../db/database.dart';

class LocaleController extends ValueNotifier<Locale?> {
  LocaleController._() : super(null);
  static final LocaleController instance = LocaleController._();

  static const _prefsKey = 'language_code';

  Future<void> load() async {
    final db = AppDatabase.instance.db;
    final rec = await AppDatabase.instance.prefsStore.record(_prefsKey).get(db);
    final code = rec != null ? rec['value'] as String? : null;
    if (code != null && code.isNotEmpty) {
      value = Locale(code);
    } else {
      final sys = PlatformDispatcher.instance.locale.languageCode;
      value = (sys == 'fr' || sys == 'en') ? Locale(sys) : const Locale('en');
    }
  }

  Future<void> setLanguageCode(String code) async {
    value = Locale(code);
    final db = AppDatabase.instance.db;
    await AppDatabase.instance.prefsStore
        .record(_prefsKey)
        .put(db, {'value': code});
  }
}

