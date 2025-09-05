import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ufrecscitizen/pages/home_page.dart';

void main() {
  testWidgets('Home page shows 4 navigation cards', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: HomePage()));

    expect(find.text('Global Stats'), findsOneWidget);
    expect(find.text('Global Results'), findsOneWidget);
    expect(find.text('Poll Office Stats'), findsOneWidget);
    expect(find.text('Poll Office Results'), findsOneWidget);
  });
}

