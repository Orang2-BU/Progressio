import 'package:flutter/material.dart';
import 'package:progressio_mobile/core/theme/app_theme.dart';
import 'package:progressio_mobile/presentation/pages/auth/login/login_page.dart';

/// ─────────────────────────────────────────────────────────────────────────────
/// Root widget — MaterialApp diconfig di sini.
/// ─────────────────────────────────────────────────────────────────────────────
class ProgressioApp extends StatelessWidget {
  const ProgressioApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Progressio',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.dopamineTheme,
      home: const LoginPage(),
    );
  }
}

