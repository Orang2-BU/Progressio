import 'package:flutter/material.dart';
import 'package:progressio_mobile/core/constants/app_colors.dart';
import 'package:progressio_mobile/core/constants/app_typography.dart';
import 'package:progressio_mobile/core/constants/app_spacing.dart';

/// ─────────────────────────────────────────────────────────────────────────────
/// Progressio — App Theme (Dopamine Design Language)
/// ─────────────────────────────────────────────────────────────────────────────
/// Seluruh ThemeData didefinisikan di sini.
/// Jangan override warna/font langsung di widget — pakai Theme.of(context).
/// ─────────────────────────────────────────────────────────────────────────────
class AppTheme {
  AppTheme._();

  static ThemeData get dopamineTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      scaffoldBackgroundColor: AppColors.canvasBg,
      primaryColor: AppColors.limePrimary,

      // ── Color Scheme ────────────────────────────────────────────────────
      colorScheme: const ColorScheme.light(
        primary: AppColors.limePrimary,
        onPrimary: AppColors.darkSlate,
        secondary: AppColors.lavenderPrimary,
        onSecondary: AppColors.surfaceWhite,
        tertiary: AppColors.coralOrange,
        surface: AppColors.surfaceWhite,
        onSurface: AppColors.textMain,
        error: AppColors.heartRed,
        onError: AppColors.surfaceWhite,
        outline: AppColors.borderColor,
      ),

      // ── Typography ──────────────────────────────────────────────────────
      fontFamily: AppTypography.bodyFont,
      textTheme: const TextTheme(
        displayLarge: TextStyle(
          fontFamily: AppTypography.headlineFont,
          fontSize: AppTypography.display1,
          fontWeight: FontWeight.w800,
          color: AppColors.textMain,
        ),
        headlineLarge: TextStyle(
          fontFamily: AppTypography.headlineFont,
          fontSize: AppTypography.heading1,
          fontWeight: FontWeight.w700,
          color: AppColors.textMain,
        ),
        headlineMedium: TextStyle(
          fontFamily: AppTypography.headlineFont,
          fontSize: AppTypography.heading2,
          fontWeight: FontWeight.w700,
          color: AppColors.textMain,
        ),
        titleLarge: TextStyle(
          fontFamily: AppTypography.headlineFont,
          fontSize: AppTypography.subtitle1,
          fontWeight: FontWeight.w600,
          color: AppColors.textMain,
        ),
        titleMedium: TextStyle(
          fontFamily: AppTypography.headlineFont,
          fontSize: AppTypography.subtitle2,
          fontWeight: FontWeight.w600,
          color: AppColors.textMain,
        ),
        bodyLarge: TextStyle(
          fontFamily: AppTypography.bodyFont,
          fontSize: AppTypography.body1,
          fontWeight: FontWeight.w400,
          color: AppColors.textMain,
        ),
        bodyMedium: TextStyle(
          fontFamily: AppTypography.bodyFont,
          fontSize: AppTypography.body2,
          fontWeight: FontWeight.w500,
          color: AppColors.textMuted,
        ),
        labelLarge: TextStyle(
          fontFamily: AppTypography.headlineFont,
          fontSize: AppTypography.subtitle1,
          fontWeight: FontWeight.w700,
          color: AppColors.darkSlate,
        ),
        labelMedium: TextStyle(
          fontFamily: AppTypography.headlineFont,
          fontSize: AppTypography.captionTag,
          fontWeight: FontWeight.w800,
          color: AppColors.textMuted,
        ),
        labelSmall: TextStyle(
          fontFamily: AppTypography.headlineFont,
          fontSize: AppTypography.captionTag,
          fontWeight: FontWeight.w800,
          color: AppColors.textMuted,
        ),
      ),

      // ── AppBar ──────────────────────────────────────────────────────────
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        foregroundColor: AppColors.darkSlate,
        elevation: 0,
        centerTitle: true,
        iconTheme: IconThemeData(color: AppColors.darkSlate),
        titleTextStyle: TextStyle(
          fontFamily: AppTypography.headlineFont,
          fontSize: AppTypography.heading2,
          fontWeight: FontWeight.w700,
          color: AppColors.textMain,
        ),
      ),

      // ── Cards ───────────────────────────────────────────────────────────
      cardTheme: CardThemeData(
        color: AppColors.surfaceWhite,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.card),
          side: const BorderSide(color: AppColors.borderColor, width: 1.2),
        ),
      ),

      // ── Elevated Button (Pill Shape) ─────────────────────────────────────
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.limePrimary,
          foregroundColor: AppColors.darkSlate,
          elevation: 0,
          minimumSize: const Size(double.infinity, 52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppRadius.pill),
          ),
          textStyle: const TextStyle(
            fontFamily: AppTypography.headlineFont,
            fontSize: AppTypography.subtitle1,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),

      // ── Outlined Button (Pill Shape) ─────────────────────────────────────
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.lavenderPrimary,
          side: const BorderSide(color: AppColors.lavenderPrimary, width: 1.5),
          minimumSize: const Size(double.infinity, 52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppRadius.pill),
          ),
          textStyle: const TextStyle(
            fontFamily: AppTypography.headlineFont,
            fontSize: AppTypography.subtitle1,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),

      // ── Input Decoration ────────────────────────────────────────────────
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.surfaceWhite,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg,
          vertical: AppSpacing.lg,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.input),
          borderSide: const BorderSide(color: AppColors.borderColor),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.input),
          borderSide: const BorderSide(color: AppColors.borderColor),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.input),
          borderSide: const BorderSide(color: AppColors.limePrimary, width: 2.0),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.input),
          borderSide: const BorderSide(color: AppColors.heartRed),
        ),
        hintStyle: const TextStyle(
          color: AppColors.textMuted,
          fontSize: AppTypography.body1,
        ),
      ),

      // ── Chip ────────────────────────────────────────────────────────────
      chipTheme: ChipThemeData(
        backgroundColor: AppColors.surfaceWhite,
        selectedColor: AppColors.limeLight,
        labelStyle: const TextStyle(
          fontFamily: AppTypography.headlineFont,
          fontSize: AppTypography.body2,
          fontWeight: FontWeight.w600,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.pill),
        ),
        side: const BorderSide(color: AppColors.borderColor),
      ),

      // ── Divider ─────────────────────────────────────────────────────────
      dividerTheme: const DividerThemeData(
        color: AppColors.borderColor,
        thickness: 1,
        space: 1,
      ),

      // ── Progress Indicator ──────────────────────────────────────────────
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: AppColors.limePrimary,
        linearTrackColor: AppColors.limeLight,
      ),
    );
  }
}
