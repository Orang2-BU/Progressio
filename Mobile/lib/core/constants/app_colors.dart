import 'package:flutter/material.dart';

/// ─────────────────────────────────────────────────────────────────────────────
/// Progressio — Color Palette (Soft Pastel Blue)
/// ─────────────────────────────────────────────────────────────────────────────
/// Warna ini di-sinkronkan dari Design System PRD.
/// Jangan pakai warna literal di widget — selalu refer ke sini.
/// ─────────────────────────────────────────────────────────────────────────────
class AppColors {
  AppColors._();

  // ── Primary ────────────────────────────────────────────────────────────────
  static const Color primary = Color(0xFF7CB8F2);        // Soft sky blue
  static const Color primaryLight = Color(0xFFA8D4FF);    // Pastel light blue
  static const Color primaryDark = Color(0xFF5A9FE0);     // Medium soft blue

  // ── Accent / Tint ─────────────────────────────────────────────────────────
  static const Color accent = Color(0xFFE8F4FD);          // Ice blue tint (bg)
  static const Color accentLight = Color(0xFFF0F7FF);     // Very light blue

  // ── Neutral / Background ──────────────────────────────────────────────────
  static const Color background = Color(0xFFF5F8FC);      // Ice blue-gray base
  static const Color surface = Color(0xFFFFFFFF);          // Card / surface white
  static const Color scaffold = Color(0xFFF5F8FC);         // Scaffold background

  // ── Text ──────────────────────────────────────────────────────────────────
  static const Color textPrimary = Color(0xFF1E293B);     // Dark slate
  static const Color textSecondary = Color(0xFF64748B);   // Medium gray
  static const Color textTertiary = Color(0xFF94A3B8);    // Light gray
  static const Color textOnPrimary = Color(0xFFFFFFFF);   // White on blue

  // ── Semantic ──────────────────────────────────────────────────────────────
  static const Color success = Color(0xFF81C995);          // Soft green
  static const Color error = Color(0xFFE57373);            // Soft red
  static const Color warning = Color(0xFFF2C97C);          // Soft amber
  static const Color info = Color(0xFF7CB8F2);             // Same as primary

  // ── Border / Divider ──────────────────────────────────────────────────────
  static const Color border = Color(0xFFE8EDF2);           // Light border
  static const Color divider = Color(0xFFE2E8F0);          // Divider line
  static const Color inputBorder = Color(0xFFE8F0FE);      // Input field border

  // ── Shadow ────────────────────────────────────────────────────────────────
  static const Color shadow = Color(0x0D000000);           // Very subtle shadow

  // ── Skill Graph Node Colors ───────────────────────────────────────────────
  static const Color nodeMastered = Color(0xFF7CB8F2);     // Soft blue
  static const Color nodeInProgress = Color(0xFF7CB8F2);   // Border only
  static const Color nodeAvailable = Color(0xFFD1D5DB);    // Dashed gray
  static const Color nodeLocked = Color(0xFFF1F5F9);       // Very light gray

  // ── Gradient ──────────────────────────────────────────────────────────────
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFFA8D4FF), Color(0xFFE8F4FD)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient splashGradient = LinearGradient(
    colors: [Color(0xFFE8F4FD), Color(0xFFFFFFFF)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );
}
