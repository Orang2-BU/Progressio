import 'package:flutter/material.dart';
import 'package:progressio_mobile/core/constants/app_colors.dart';
import 'package:progressio_mobile/core/constants/app_typography.dart';
import 'package:progressio_mobile/core/constants/app_spacing.dart';

/// ─────────────────────────────────────────────────────────────────────────────
/// Progressio — App Theme
/// ─────────────────────────────────────────────────────────────────────────────
/// Seluruh ThemeData didefinisikan di sini.
/// Jangan override warna/font langsung di widget — pakai Theme.of(context).
/// ─────────────────────────────────────────────────────────────────────────────
class AppTheme {
  AppTheme._();

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      scaffoldBackgroundColor: AppColors.scaffold,

      // ── Color Scheme ────────────────────────────────────────────────────
      colorScheme: const ColorScheme.light(
        primary: AppColors.primary,
        onPrimary: AppColors.textOnPrimary,
        secondary: AppColors.primaryLight,
        onSecondary: AppColors.textPrimary,
        tertiary: AppColors.primaryDark,
        surface: AppColors.surface,
        onSurface: AppColors.textPrimary,
        error: AppColors.error,
        onError: AppColors.textOnPrimary,
        outline: AppColors.border,
      ),

      // ── Typography ──────────────────────────────────────────────────────
      fontFamily: AppTypography.bodyFont,
      textTheme: const TextTheme(
        headlineLarge: TextStyle(
          fontFamily: AppTypography.headlineFont,
          fontSize: AppTypography.heading1,
          fontWeight: FontWeight.w700,
          color: AppColors.textPrimary,
        ),
        headlineMedium: TextStyle(
          fontFamily: AppTypography.headlineFont,
          fontSize: AppTypography.heading2,
          fontWeight: FontWeight.w700,
          color: AppColors.textPrimary,
        ),
        headlineSmall: TextStyle(
          fontFamily: AppTypography.headlineFont,
          fontSize: AppTypography.heading3,
          fontWeight: FontWeight.w600,
          color: AppColors.textPrimary,
        ),
        titleLarge: TextStyle(
          fontFamily: AppTypography.headlineFont,
          fontSize: AppTypography.heading4,
          fontWeight: FontWeight.w600,
          color: AppColors.textPrimary,
        ),
        titleMedium: TextStyle(
          fontSize: AppTypography.subtitle1,
          fontWeight: FontWeight.w600,
          color: AppColors.textPrimary,
        ),
        titleSmall: TextStyle(
          fontSize: AppTypography.subtitle2,
          fontWeight: FontWeight.w600,
          color: AppColors.textPrimary,
        ),
        bodyLarge: TextStyle(
          fontSize: AppTypography.body1,
          fontWeight: FontWeight.w400,
          color: AppColors.textPrimary,
        ),
        bodyMedium: TextStyle(
          fontSize: AppTypography.body2,
          fontWeight: FontWeight.w400,
          color: AppColors.textSecondary,
        ),
        labelLarge: TextStyle(
          fontSize: AppTypography.body1,
          fontWeight: FontWeight.w600,
          color: AppColors.textOnPrimary,
        ),
        labelMedium: TextStyle(
          fontSize: AppTypography.caption,
          fontWeight: FontWeight.w500,
          color: AppColors.textSecondary,
        ),
        labelSmall: TextStyle(
          fontSize: AppTypography.overline,
          fontWeight: FontWeight.w400,
          color: AppColors.textTertiary,
        ),
      ),

      // ── AppBar ──────────────────────────────────────────────────────────
      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.textPrimary,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          fontFamily: AppTypography.headlineFont,
          fontSize: AppTypography.heading4,
          fontWeight: FontWeight.w600,
          color: AppColors.textPrimary,
        ),
      ),

      // ── Cards ───────────────────────────────────────────────────────────
      cardTheme: CardThemeData(
        color: AppColors.surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.card),
        ),
        shadowColor: AppColors.shadow,
      ),

      // ── Elevated Button ─────────────────────────────────────────────────
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: AppColors.textOnPrimary,
          elevation: 0,
          minimumSize: const Size(double.infinity, 52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppRadius.button),
          ),
          textStyle: const TextStyle(
            fontFamily: AppTypography.bodyFont,
            fontSize: AppTypography.subtitle1,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),

      // ── Outlined Button ─────────────────────────────────────────────────
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.primary,
          side: const BorderSide(color: AppColors.primary, width: 1.5),
          minimumSize: const Size(double.infinity, 52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppRadius.button),
          ),
          textStyle: const TextStyle(
            fontFamily: AppTypography.bodyFont,
            fontSize: AppTypography.subtitle1,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),

      // ── Input Decoration ────────────────────────────────────────────────
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.surface,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg,
          vertical: AppSpacing.lg,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.input),
          borderSide: const BorderSide(color: AppColors.inputBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.input),
          borderSide: const BorderSide(color: AppColors.inputBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.input),
          borderSide: const BorderSide(color: AppColors.primary, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.input),
          borderSide: const BorderSide(color: AppColors.error),
        ),
        hintStyle: const TextStyle(
          color: AppColors.textTertiary,
          fontSize: AppTypography.body1,
        ),
      ),

      // ── Bottom Nav ──────────────────────────────────────────────────────
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: AppColors.surface,
        selectedItemColor: AppColors.primary,
        unselectedItemColor: AppColors.textTertiary,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
        selectedLabelStyle: TextStyle(
          fontSize: AppTypography.caption,
          fontWeight: FontWeight.w600,
        ),
        unselectedLabelStyle: TextStyle(
          fontSize: AppTypography.caption,
          fontWeight: FontWeight.w400,
        ),
      ),

      // ── Chip ────────────────────────────────────────────────────────────
      chipTheme: ChipThemeData(
        backgroundColor: AppColors.accent,
        selectedColor: AppColors.primary,
        labelStyle: const TextStyle(
          fontSize: AppTypography.body2,
          fontWeight: FontWeight.w500,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.pill),
        ),
        side: BorderSide.none,
      ),

      // ── Divider ─────────────────────────────────────────────────────────
      dividerTheme: const DividerThemeData(
        color: AppColors.divider,
        thickness: 1,
        space: 1,
      ),

      // ── Progress Indicator ──────────────────────────────────────────────
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: AppColors.primary,
        linearTrackColor: AppColors.accent,
      ),
    );
  }
}
