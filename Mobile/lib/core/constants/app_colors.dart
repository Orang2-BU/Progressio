import 'package:flutter/material.dart';

/// ─────────────────────────────────────────────────────────────────────────────
/// Progressio — Color Palette (Neo-Dopamine Gamified)
/// ─────────────────────────────────────────────────────────────────────────────
/// Warna ini di-sinkronkan dari DESIGN.md (Dopamine Design Language).
/// Jangan pakai warna literal di widget — selalu refer ke sini.
/// ─────────────────────────────────────────────────────────────────────────────
class AppColors {
  AppColors._();

  // ── Brand Lime Dopamine ───────────────────────────────────────────────────
  static const Color limePrimary = Color(0xFFB5F942);     // Warna brand utama
  static const Color limeDeep = Color(0xFF8DE319);         // Akhir gradien, border highlight
  static const Color limeLight = Color(0xFFE8FDC9);        // Background kartu sub-fitur

  // ── High Contrast Dark Anchors ────────────────────────────────────────────
  static const Color darkSlate = Color(0xFF14161D);        // Hero card, navbar, headline
  static const Color darkCard = Color(0xFF1D2027);         // Surface kartu dark sekunder

  // ── Playful Dopamine Accents ──────────────────────────────────────────────
  static const Color lavenderBg = Color(0xFFEDE6FF);       // Background kartu kategori
  static const Color lavenderPrimary = Color(0xFF7B4FE3);  // Badge "Hot", status pill aktif
  static const Color coralOrange = Color(0xFFFF623E);      // Streak fire 🔥, banner challenge
  static const Color sunYellow = Color(0xFFFDE93A);        // Tag poin, XP token, bintang ⭐

  // ── Background & Surfaces ─────────────────────────────────────────────────
  static const Color canvasBg = Color(0xFFF7FAF4);         // Background halaman (off-white gading)
  static const Color surfaceWhite = Color(0xFFFFFFFF);     // Background kartu, modal, list item
  static const Color borderColor = Color(0xFFEAEFE3);      // Outline kartu halus, pembatas

  // ── Text ──────────────────────────────────────────────────────────────────
  static const Color textMain = Color(0xFF111317);         // Judul utama (Super High Contrast)
  static const Color textMuted = Color(0xFF727782);        // Teks sekunder, deskripsi, placeholder

  // ── Gamification Semantic ─────────────────────────────────────────────────
  static const Color heartRed = Color(0xFFFF4757);         // Sisa nyawa & jawaban salah
  static const Color streakFire = Color(0xFFFF623E);       // Ikon api streak & countdown
  static const Color xpGold = Color(0xFFFFC800);           // XP counter, level bar, badge
  static const Color successGreen = Color(0xFF22C55E);     // Jawaban benar, skill verified
  static const Color lockedGray = Color(0xFFCBD5E1);       // Node terkunci, tombol belum aktif
  static const Color blockchainCyan = Color(0xFF00D2D3);   // Badge verifikasi blockchain

  // ── Feedback Backgrounds ──────────────────────────────────────────────────
  static const Color feedbackSuccessBg = Color(0xFFE8FDC9); // Sheet jawaban benar
  static const Color feedbackErrorBg = Color(0xFFFFEAEA);   // Sheet jawaban salah

  // ── Gradient ──────────────────────────────────────────────────────────────
  static const LinearGradient limeHeaderGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [Color(0xFFB8F944), Color(0xFFD4FFA0), Color(0xFFF7FAF4)],
    stops: [0.0, 0.45, 1.0],
  );

  static const LinearGradient darkCardGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFF1A1C23), Color(0xFF111216)],
  );

  static const LinearGradient lavenderCardGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFFEDE6FF), Color(0xFFE4D7FF)],
  );
}
