import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:progressio_mobile/app/app.dart';
import 'package:progressio_mobile/presentation/pages/auth/login/login_page.dart';

void main() {
  testWidgets('ProgressioApp smoke test — renders LoginPage with form elements', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1080, 2400);
    tester.view.devicePixelRatio = 2.0;
    addTearDown(tester.view.resetPhysicalSize);

    // Build root app ProgressioApp
    await tester.pumpWidget(const ProgressioApp());
    await tester.pumpAndSettle();

    // Verify Brand / Header text
    expect(find.text('PROGRESSIO'), findsOneWidget);
    expect(find.text('V2.4 NEO'), findsOneWidget);
    expect(find.text('Selamat Datang!'), findsOneWidget);

    // Verify Inputs exist
    expect(find.text('Email Belajar'), findsOneWidget);
    expect(find.text('Kata Sandi'), findsOneWidget);

    // Verify CTA Buttons
    expect(find.text('Masuk Sekarang'), findsOneWidget);
    expect(find.text('Lanjutkan dengan Google'), findsOneWidget);
    expect(find.text('Daftar Gratis'), findsOneWidget);
  });

  testWidgets('LoginPage validation test — empty submission triggers validation error', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1080, 2400);
    tester.view.devicePixelRatio = 2.0;
    addTearDown(tester.view.resetPhysicalSize);

    await tester.pumpWidget(const MaterialApp(
      home: LoginPage(),
    ));
    await tester.pumpAndSettle();

    // Tap submit button without filling fields
    final submitButton = find.text('Masuk Sekarang');
    await tester.tap(submitButton);
    await tester.pumpAndSettle();

    // Verify error messages appear (case-sensitive matching)
    expect(find.text('Email wajib diisi'), findsOneWidget);
    expect(find.text('Kata sandi wajib diisi'), findsOneWidget);
  });
}
