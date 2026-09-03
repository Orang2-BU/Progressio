/// ─────────────────────────────────────────────────────────────────────────────
/// Progressio — Spacing & Sizing Constants (Dopamine Design System)
/// ─────────────────────────────────────────────────────────────────────────────
class AppSpacing {
  AppSpacing._();

  // ── Padding / Margin ──────────────────────────────────────────────────────
  static const double xs = 4.0;    // Icon padding, tag spacing
  static const double sm = 8.0;    // Internal chip padding, compact row gap
  static const double md = 12.0;   // Inner card padding, list gap
  static const double lg = 16.0;   // Screen horizontal padding, section gap
  static const double xl = 24.0;   // Major card gap, hero spacing
  static const double xxl = 32.0;  // Large section separation

  // ── Screen Horizontal Padding ─────────────────────────────────────────────
  static const double screenPadding = 16.0;

  // ── Card Spacing ──────────────────────────────────────────────────────────
  static const double cardSpacing = 12.0;
  static const double sectionSpacing = 24.0;
}

/// ─────────────────────────────────────────────────────────────────────────────
/// Progressio — Border Radius Constants (Dopamine Pill Geometry)
/// ─────────────────────────────────────────────────────────────────────────────
class AppRadius {
  AppRadius._();

  // ── Generic Scale ─────────────────────────────────────────────────────────
  static const double sm = 8.0;
  static const double md = 12.0;
  static const double lg = 16.0;
  static const double xl = 20.0;
  static const double xxl = 24.0;

  // ── Specific (Dopamine Geometry) ──────────────────────────────────────────
  static const double card = 24.0;           // Modular cards (grid & list)
  static const double heroBanner = 26.0;     // Hero dark card banner
  static const double button = 999.0;        // Pill / capsule buttons
  static const double pill = 999.0;          // Pill shape (badges, search, pills)
  static const double input = 16.0;          // Input fields & code boxes
  static const double floatingNav = 36.0;    // Floating bottom nav bar
  static const double bottomSheet = 24.0;    // Bottom sheet top corners
  static const double interestChip = 20.0;   // Interest selector chips
  static const double iconBox = 14.0;        // Ikon box di dalam card
}
