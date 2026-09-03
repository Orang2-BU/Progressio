import 'package:flutter/material.dart';
import 'package:progressio_mobile/core/constants/app_colors.dart';
import 'package:progressio_mobile/core/constants/app_typography.dart';
import 'package:progressio_mobile/core/constants/app_spacing.dart';

/// ─────────────────────────────────────────────────────────────────────────────
/// Splash Screen — Halaman pertama saat app dibuka.
/// ─────────────────────────────────────────────────────────────────────────────
/// Background darkSlate, logo lime bersinar, tagline fade-in.
/// Sesuai DESIGN.md Section 6.1.
/// ─────────────────────────────────────────────────────────────────────────────
class SplashPage extends StatelessWidget {
  const SplashPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        color: AppColors.darkSlate,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Logo
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: AppColors.limePrimary,
                borderRadius: BorderRadius.circular(AppRadius.xxl),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.limePrimary.withOpacity(0.45),
                    blurRadius: 24,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
              child: const Center(
                child: Text(
                  'P',
                  style: TextStyle(
                    fontFamily: AppTypography.headlineFont,
                    fontSize: 40,
                    fontWeight: FontWeight.w800,
                    color: AppColors.darkSlate,
                  ),
                ),
              ),
            ),
            const SizedBox(height: AppSpacing.xl),
            // App Name
            const Text(
              'Progressio',
              style: TextStyle(
                fontFamily: AppTypography.headlineFont,
                fontSize: AppTypography.heading1,
                fontWeight: FontWeight.w700,
                color: AppColors.limePrimary,
              ),
            ),
            const SizedBox(height: AppSpacing.sm),
            // Tagline
            const Text(
              'Turning Progress Into Proof',
              style: TextStyle(
                fontFamily: AppTypography.bodyFont,
                fontSize: AppTypography.body1,
                color: AppColors.textMuted,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
