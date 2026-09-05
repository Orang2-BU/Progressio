/// ─────────────────────────────────────────────────────────────────────────────
/// Progressio — API Constants
/// ─────────────────────────────────────────────────────────────────────────────
class ApiConstants {
  ApiConstants._();

  // Ganti saat deploy ke production
  static const String baseUrl = 'http://10.0.2.2:8000';  // Android emulator → localhost
  static const String apiVersion = '/api/v1';

  // ── Auth ────────────────────────────────────────────────────────────
  static const String register = '$apiVersion/auth/register';
  static const String login = '$apiVersion/auth/login';
  static const String refreshToken = '$apiVersion/auth/refresh';
  static const String passwordReset = '$apiVersion/auth/password-reset';
  static const String me = '$apiVersion/auth/me';

  // ── Career Tracks ──────────────────────────────────────────────────
  static const String careerTracks = '$apiVersion/career-tracks';

  // ── Competencies ───────────────────────────────────────────────────
  static const String competencies = '$apiVersion/competencies';

  // ── Skills ─────────────────────────────────────────────────────────
  static const String skills = '$apiVersion/skills';

  // ── Learning ───────────────────────────────────────────────────────
  static const String lessons = '$apiVersion/lessons';
  static const String learningPath = '$apiVersion/learning-path';
  static const String progress = '$apiVersion/progress';
  static const String roadmap = '$apiVersion/roadmap';

  // ── Assessments ────────────────────────────────────────────────────
  static const String assessments = '$apiVersion/assessments';
  static const String diagnostics = '$apiVersion/diagnostics';

  // ── Credentials ────────────────────────────────────────────────────
  static const String credentials = '$apiVersion/credentials';
  static const String credentialIssue = '$apiVersion/credentials/issue';

  // ── Verification ───────────────────────────────────────────────────
  static const String verify = '$apiVersion/verify';

  // ── Health ─────────────────────────────────────────────────────────
  static const String health = '$apiVersion/health/';
}
