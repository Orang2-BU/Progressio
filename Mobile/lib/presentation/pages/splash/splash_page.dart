import 'package:flutter/material.dart';
import 'package:progressio_mobile/core/constants/app_colors.dart';
import 'package:progressio_mobile/core/constants/app_typography.dart';

/// ─────────────────────────────────────────────────────────────────────────────
/// Splash Screen — Halaman pertama saat app dibuka.
/// ─────────────────────────────────────────────────────────────────────────────
class SplashPage extends StatelessWidget {
  const SplashPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: AppColors.splashGradient,
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Logo
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: AppColors.primary,
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Center(
                child: Text(
                  'P',
                  style: TextStyle(
                    fontFamily: AppTypography.headlineFont,
                    fontSize: 40,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textOnPrimary,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 20),
            // App Name
            const Text(
              'Progressio',
              style: TextStyle(
                fontFamily: AppTypography.headlineFont,
                fontSize: AppTypography.heading1,
                fontWeight: FontWeight.w700,
                color: AppColors.primaryDark,
              ),
            ),
            const SizedBox(height: 8),
            // Tagline
            const Text(
              'Turning Progress Into Proof',
              style: TextStyle(
                fontFamily: AppTypography.bodyFont,
                fontSize: AppTypography.body1,
                color: AppColors.textTertiary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
