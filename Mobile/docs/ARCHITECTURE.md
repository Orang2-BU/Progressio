# 📁 Progressio Mobile — Panduan Arsitektur & Struktur Folder

> **Aturan Utama:** Jangan pernah naruh file sembarangan. Setiap file HARUS masuk ke folder yang benar sesuai panduan ini. Kalau foldernya belum ada, **buat dulu** foldernya, baru buat filenya.
>
> **Dokumen terkait:**
> - [PRD Mobile](PRD_MOBILE.md) — Spesifikasi fitur, halaman, gamifikasi
> - [AGENTS.md](../AGENTS.md) — Instruksi AI untuk coding style & konvensi
> - [Platform Native](NATIVE_PLATFORMS.md) — Kapan menyentuh folder `android/` dan `ios/`

---

## 🏗️ Arsitektur: Clean Architecture (3 Layer)

```
┌──────────────────────────────────────────────────────┐
│                   PRESENTATION                        │
│       (Pages, Widgets, BLoC/Cubit, Navigation)        │
├──────────────────────────────────────────────────────┤
│                      DOMAIN                           │
│      (Entity, UseCase, Repository Interface)          │
├──────────────────────────────────────────────────────┤
│                       DATA                            │
│   (Model, Repository Impl, DataSource, API)           │
└──────────────────────────────────────────────────────┘
```

Aliran data: **Page → BLoC/Cubit → UseCase → Repository → DataSource → API/Local**

### Aturan Dependensi Layer

```
PRESENTATION  →  Hanya tahu UI + BLoC. Tidak boleh import dari data/.
DOMAIN        →  Bisnis murni. Tidak boleh import Flutter atau package luar.
DATA          →  Implementasi akses data. Boleh import domain/, tidak boleh import presentation/.
```

```
presentation/ → domain/     ✅
presentation/ → data/       ❌ DILARANG
data/         → domain/     ✅ (implement interface repository)
data/         → presentation/ ❌ DILARANG
domain/       → flutter     ❌ DILARANG (hanya Dart core)
```

---

## ⚙️ Stack Teknologi

| Aspek | Pilihan | Package |
|---|---|---|
| Framework | Flutter (Dart SDK ^3.11.0) | — |
| State Management | BLoC / Cubit | `flutter_bloc` |
| Navigasi | GoRouter (declarative) | `go_router` |
| HTTP Client | Dio | `dio` |
| Dependency Injection | Service Locator | `get_it` + `injectable` |
| Secure Storage | JWT token, sensitive data | `flutter_secure_storage` |
| Local Storage | Settings, cache flag | `shared_preferences` |
| Linting | Flutter recommended | `flutter_lints` |

---

## 📂 Struktur Folder Lengkap

```text
lib/
├── main.dart                          ← Entry point, JANGAN taruh logic di sini
├── app/
│   └── app.dart                       ← MaterialApp + MultiBlocProvider + GoRouter
│
├── config/                            ← Konfigurasi environment, flavor, dll
│
├── core/                              ← Fondasi yang dipakai SELURUH app
│   ├── constants/                     ← Nilai-nilai tetap (warna, spacing, API URL)
│   │   ├── constants.dart             ← Barrel export — import ini saja
│   │   ├── app_colors.dart            ← Palet warna (JANGAN hardcode warna di widget)
│   │   ├── app_typography.dart        ← Ukuran & family font
│   │   ├── app_spacing.dart           ← Padding, margin, border radius
│   │   ├── app_strings.dart           ← Semua teks UI (untuk i18n nanti)
│   │   ├── api_constants.dart         ← URL endpoint backend
│   │   └── gamification_constants.dart ← XP values, level thresholds, heart config
│   │
│   ├── theme/                         ← ThemeData Flutter
│   │   └── app_theme.dart             ← SATU-SATUNYA tempat definisi theme
│   │
│   ├── network/                       ← HTTP client, interceptor, dio setup
│   │   ├── api_client.dart            ← Dio instance & konfigurasi
│   │   ├── dio_interceptor.dart       ← Logging, error handling interceptor
│   │   └── token_interceptor.dart     ← Auto-refresh JWT token
│   │
│   ├── storage/                       ← Local storage (SharedPrefs, SecureStorage)
│   │   ├── local_storage.dart         ← SharedPreferences wrapper
│   │   └── secure_storage.dart        ← flutter_secure_storage wrapper (JWT)
│   │
│   ├── utils/                         ← Helper/utility function
│   │   ├── date_formatter.dart        ← Format tanggal Bahasa Indonesia
│   │   ├── validators.dart            ← Validasi email, password, dll
│   │   └── xp_calculator.dart         ← Kalkulasi XP & level
│   │
│   └── errors/                        ← Custom exception & failure classes
│       ├── app_exception.dart         ← Exception types
│       └── failure.dart               ← Failure sealed class (Server, Network, Cache)
│
├── data/                              ← IMPLEMENTASI akses data
│   ├── models/                        ← Model JSON (fromJson/toJson)
│   │   ├── user_model.dart
│   │   ├── career_track_model.dart
│   │   ├── competency_model.dart
│   │   ├── skill_model.dart
│   │   ├── lesson_model.dart
│   │   ├── assessment_model.dart
│   │   ├── submission_model.dart
│   │   ├── credential_model.dart
│   │   ├── diagnostic_model.dart
│   │   ├── gamification_model.dart    ← XP, streak, hearts, badge, daily goal
│   │   ├── leaderboard_model.dart
│   │   ├── friend_model.dart
│   │   └── notification_model.dart
│   │
│   ├── repositories/                  ← Implementasi repository (memanggil datasource)
│   │   ├── auth_repository_impl.dart
│   │   ├── career_track_repository_impl.dart
│   │   ├── learning_repository_impl.dart
│   │   ├── assessment_repository_impl.dart
│   │   ├── credential_repository_impl.dart
│   │   ├── gamification_repository_impl.dart
│   │   ├── social_repository_impl.dart
│   │   └── notification_repository_impl.dart
│   │
│   └── datasources/
│       ├── remote/                    ← Panggilan API ke backend Django
│       │   ├── auth_remote_datasource.dart
│       │   ├── career_track_remote_datasource.dart
│       │   ├── learning_remote_datasource.dart
│       │   ├── assessment_remote_datasource.dart
│       │   ├── credential_remote_datasource.dart
│       │   ├── gamification_remote_datasource.dart
│       │   ├── social_remote_datasource.dart
│       │   └── notification_remote_datasource.dart
│       └── local/                     ← Cache lokal / offline data
│           ├── auth_local_datasource.dart
│           ├── lesson_local_datasource.dart   ← Cache lesson untuk offline
│           └── settings_local_datasource.dart
│
├── domain/                            ← KONTRAK bisnis (tidak boleh import Flutter)
│   ├── entities/                      ← Object bisnis murni (bukan model JSON)
│   │   ├── user.dart
│   │   ├── career_track.dart
│   │   ├── competency.dart
│   │   ├── skill.dart
│   │   ├── lesson.dart
│   │   ├── assessment.dart
│   │   ├── submission.dart
│   │   ├── credential.dart
│   │   ├── diagnostic.dart
│   │   ├── gamification.dart          ← XP, Streak, Hearts, Badge, Level
│   │   ├── leaderboard_entry.dart
│   │   ├── friend.dart
│   │   └── notification.dart
│   │
│   ├── repositories/                  ← Abstract class / interface repository
│   │   ├── auth_repository.dart
│   │   ├── career_track_repository.dart
│   │   ├── learning_repository.dart
│   │   ├── assessment_repository.dart
│   │   ├── credential_repository.dart
│   │   ├── gamification_repository.dart
│   │   ├── social_repository.dart
│   │   └── notification_repository.dart
│   │
│   └── usecases/                      ← Satu class = satu aksi bisnis
│       ├── auth/
│       │   ├── login_usecase.dart
│       │   ├── register_usecase.dart
│       │   └── logout_usecase.dart
│       ├── learning/
│       │   ├── get_career_tracks_usecase.dart
│       │   ├── get_learning_path_usecase.dart
│       │   ├── get_lesson_usecase.dart
│       │   ├── complete_lesson_usecase.dart
│       │   └── submit_checkpoint_usecase.dart
│       ├── assessment/
│       │   ├── get_assessment_usecase.dart
│       │   ├── submit_assessment_usecase.dart
│       │   ├── get_diagnostic_usecase.dart
│       │   └── submit_diagnostic_usecase.dart
│       ├── gamification/
│       │   ├── get_xp_usecase.dart
│       │   ├── get_streak_usecase.dart
│       │   ├── get_hearts_usecase.dart
│       │   └── get_daily_challenge_usecase.dart
│       ├── credential/
│       │   ├── get_credentials_usecase.dart
│       │   └── get_credential_detail_usecase.dart
│       └── social/
│           ├── get_leaderboard_usecase.dart
│           ├── get_friends_usecase.dart
│           └── add_friend_usecase.dart
│
└── presentation/                      ← SEMUA yang berhubungan dengan UI
    ├── blocs/                         ← BLoC/Cubit GLOBAL (selalu tersedia di app)
    │   ├── auth/
    │   │   ├── auth_bloc.dart
    │   │   ├── auth_event.dart
    │   │   └── auth_state.dart
    │   ├── user/
    │   │   ├── user_cubit.dart
    │   │   └── user_state.dart
    │   ├── gamification/
    │   │   ├── gamification_cubit.dart  ← XP, level, streak, hearts, daily goal
    │   │   └── gamification_state.dart
    │   ├── notification/
    │   │   ├── notification_cubit.dart
    │   │   └── notification_state.dart
    │   └── settings/
    │       ├── settings_cubit.dart
    │       └── settings_state.dart
    │
    ├── widgets/                       ← Widget REUSABLE yang dipakai di banyak halaman
    │   ├── common/                    ← Widget umum
    │   │   ├── app_bar_custom.dart
    │   │   ├── loading_shimmer.dart    ← Skeleton loading (BUKAN spinner polos)
    │   │   ├── empty_state.dart       ← Ilustrasi + pesan + CTA
    │   │   ├── error_state.dart       ← Pesan error + tombol retry
    │   │   └── offline_banner.dart    ← Banner "Tidak ada koneksi"
    │   ├── buttons/                   ← Tombol-tombol custom
    │   ├── cards/                     ← Card custom
    │   │   ├── career_track_card.dart
    │   │   ├── skill_node.dart        ← Node di learning path graph
    │   │   ├── lesson_step_card.dart
    │   │   ├── credential_card.dart
    │   │   ├── daily_challenge_card.dart
    │   │   └── leaderboard_entry.dart
    │   ├── inputs/                    ← Text field custom, search bar, dll
    │   ├── dialogs/                   ← Dialog, bottom sheet, snackbar custom
    │   ├── indicators/                ← Progress bar, circular ring, badge
    │   │   ├── xp_bar.dart            ← XP progress ke level berikutnya
    │   │   ├── hearts_display.dart    ← Tampilan sisa hearts ❤️
    │   │   ├── streak_counter.dart    ← Streak count + ikon api 🔥
    │   │   ├── mastery_ring.dart      ← Radial progress mastery skill
    │   │   └── level_badge.dart       ← Badge level user
    │   └── gamification/              ← Animasi & overlay gamifikasi
    │       ├── confetti_overlay.dart   ← Animasi confetti (assessment lulus)
    │       ├── level_up_overlay.dart   ← Full-screen overlay level up
    │       ├── xp_float_animation.dart ← Teks "+10 XP" float ke atas
    │       └── heart_break_animation.dart ← Animasi heart pecah
    │
    ├── navigation/                    ← Router, bottom nav, route constants
    │   ├── app_router.dart            ← GoRouter config + semua route
    │   └── bottom_nav_shell.dart      ← ShellRoute bottom navigation
    │
    └── pages/                         ← SETIAP halaman punya folder sendiri
        │
        │── splash/
        │   └── splash_page.dart
        │
        │── onboarding/
        │   └── onboarding_page.dart
        │
        │── interest_selector/         ← Pilih topik minat user
        │   ├── interest_selector_page.dart
        │   └── widgets/
        │       └── interest_chip.dart
        │
        │── auth/
        │   ├── login/
        │   │   ├── login_page.dart
        │   │   └── widgets/
        │   │       └── login_form.dart
        │   ├── register/
        │   │   ├── register_page.dart
        │   │   └── widgets/
        │   │       └── role_selector.dart
        │   └── forgot_password/
        │       └── forgot_password_page.dart
        │
        │── home/                      ← ⭐ Hub utama setelah login
        │   ├── home_page.dart
        │   ├── bloc/
        │   │   ├── home_cubit.dart
        │   │   └── home_state.dart
        │   └── widgets/
        │       ├── stats_row.dart
        │       ├── current_track_card.dart
        │       ├── daily_goal_ring.dart
        │       └── track_recommendation_list.dart
        │
        │── career_tracks/
        │   └── career_tracks_page.dart
        │
        │── career_track_detail/
        │   └── career_track_detail_page.dart
        │
        │── diagnostic/               ← Tes awal ukur kemampuan
        │   ├── diagnostic_page.dart
        │   ├── bloc/
        │   │   ├── diagnostic_bloc.dart
        │   │   ├── diagnostic_event.dart
        │   │   └── diagnostic_state.dart
        │   └── widgets/
        │       └── diagnostic_question_card.dart
        │
        │── diagnostic_result/        ← Hasil diagnostic + rekomendasi
        │   └── diagnostic_result_page.dart
        │
        │── learning_path/            ← ⭐ Visual skill graph (peta belajar)
        │   ├── learning_path_page.dart
        │   ├── bloc/
        │   │   ├── learning_path_cubit.dart
        │   │   └── learning_path_state.dart
        │   └── widgets/
        │       ├── skill_node_widget.dart
        │       ├── path_connector.dart
        │       └── checkpoint_node.dart
        │
        │── skill_detail/
        │   └── skill_detail_page.dart
        │
        │── lesson/                   ← ⭐ Konten pembelajaran + checkpoint
        │   ├── lesson_page.dart
        │   ├── bloc/
        │   │   ├── lesson_cubit.dart
        │   │   └── lesson_state.dart
        │   └── widgets/
        │       ├── reading_content.dart      ← Render markdown + code
        │       ├── video_player_card.dart     ← Video player
        │       ├── multiple_choice.dart       ← Soal pilihan ganda
        │       ├── fill_in_blank.dart         ← Isi kode yang kosong
        │       ├── arrange_code.dart          ← Susun baris kode (drag & drop)
        │       ├── true_false.dart            ← Soal benar/salah
        │       ├── match_pairs.dart           ← Cocokkan pasangan
        │       └── answer_feedback.dart       ← Feedback benar/salah + XP
        │
        │── assessment/               ← ⭐ Evaluasi akhir per skill
        │   ├── assessment_page.dart
        │   ├── bloc/
        │   │   ├── assessment_bloc.dart
        │   │   ├── assessment_event.dart
        │   │   └── assessment_state.dart
        │   └── widgets/
        │       └── answer_option_card.dart
        │
        │── assessment_result/
        │   └── assessment_result_page.dart
        │
        │── daily_challenge/          ← Tantangan harian bonus XP
        │   ├── daily_challenge_page.dart
        │   ├── bloc/
        │   │   ├── daily_challenge_bloc.dart
        │   │   ├── daily_challenge_event.dart
        │   │   └── daily_challenge_state.dart
        │   └── widgets/
        │       └── challenge_progress_dots.dart
        │
        │── leaderboard/              ← Peringkat XP mingguan/bulanan
        │   ├── leaderboard_page.dart
        │   └── widgets/
        │       └── podium_top_three.dart
        │
        │── friends/                  ← Daftar teman + invite
        │   ├── friends_page.dart
        │   └── widgets/
        │       └── friend_request_card.dart
        │
        │── credentials/
        │   └── credentials_page.dart
        │
        │── credential_detail/
        │   ├── credential_detail_page.dart
        │   └── widgets/
        │       ├── certificate_preview.dart
        │       └── blockchain_proof_section.dart
        │
        │── share_credential/        ← Preview share ke social media
        │   └── share_credential_page.dart
        │
        │── verification/
        │   └── verification_page.dart
        │
        │── roadmap/
        │   └── roadmap_page.dart
        │
        │── profile/
        │   ├── profile_page.dart
        │   └── widgets/
        │       ├── stats_grid.dart
        │       ├── badge_collection.dart
        │       └── activity_heatmap.dart
        │
        │── settings/                 ← Pengaturan notifikasi, tampilan, akun
        │   └── settings_page.dart
        │
        └── notification/            ← Daftar notifikasi
            └── notification_page.dart
```

---

## 🧠 State Management: BLoC / Cubit

### Kapan Pakai BLoC vs Cubit

| Gunakan | Kapan | Contoh |
|---|---|---|
| **Cubit** | State sederhana, tidak perlu event terpisah | `HomeCubit`, `UserCubit`, `SettingsCubit` |
| **BLoC** | State kompleks, event-driven, butuh transformasi event | `AuthBloc`, `AssessmentBloc`, `DiagnosticBloc` |

### Scope: Global vs Per-Halaman

| Scope | Ditempatkan di | Lifetime | Contoh |
|---|---|---|---|
| **Global** | `presentation/blocs/` + wrap di `app.dart` via `MultiBlocProvider` | Selama app hidup | `AuthBloc`, `GamificationCubit`, `UserCubit`, `NotificationCubit`, `SettingsCubit` |
| **Per-halaman** | `presentation/pages/<nama>/bloc/` + wrap via `BlocProvider` di route | Saat halaman dibuka | `LessonCubit`, `AssessmentBloc`, `DiagnosticBloc`, `HomeCubit` |

### Inisialisasi Global BLoC

```dart
// app.dart
class ProgressioApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (_) => getIt<AuthBloc>()),
        BlocProvider(create: (_) => getIt<UserCubit>()),
        BlocProvider(create: (_) => getIt<GamificationCubit>()),
        BlocProvider(create: (_) => getIt<NotificationCubit>()),
        BlocProvider(create: (_) => getIt<SettingsCubit>()),
      ],
      child: MaterialApp.router(
        theme: AppTheme.lightTheme,
        routerConfig: appRouter,
      ),
    );
  }
}
```

### Pola State

```dart
// Gunakan sealed class
sealed class HomeState {}
class HomeInitial extends HomeState {}
class HomeLoading extends HomeState {}
class HomeLoaded extends HomeState {
  final UserProfile user;
  final GamificationData gamification;
  final List<CareerTrack> recommendations;
  HomeLoaded({required this.user, required this.gamification, required this.recommendations});
}
class HomeError extends HomeState {
  final String message;
  HomeError(this.message);
}
```

### Yang DILARANG

```
❌ SALAH:  Panggil API langsung dari BLoC/Cubit
✅ BENAR:  BLoC/Cubit → UseCase → Repository → DataSource → API

❌ SALAH:  setState() untuk state kompleks
✅ BENAR:  Pakai BLoC/Cubit

❌ SALAH:  Simpan state di global variable
✅ BENAR:  Pakai BLoC/Cubit yang di-provide via BlocProvider
```

---

## 📏 Aturan yang WAJIB Diikuti

### 1. Warna
```
❌ SALAH:  Color(0xFF7CB8F2)  ← di dalam widget
✅ BENAR:  AppColors.primary   ← dari constants
```
Semua warna HARUS diambil dari `lib/core/constants/app_colors.dart`.

### 2. Font & Ukuran
```
❌ SALAH:  fontSize: 16
✅ BENAR:  fontSize: AppTypography.subtitle1
```
Semua font size diambil dari `app_typography.dart`, semua font family dari theme.
Atau gunakan `Theme.of(context).textTheme.titleLarge` untuk TextStyle lengkap.

### 3. Spacing & Radius
```
❌ SALAH:  padding: EdgeInsets.all(16)
✅ BENAR:  padding: EdgeInsets.all(AppSpacing.lg)

❌ SALAH:  BorderRadius.circular(16)
✅ BENAR:  BorderRadius.circular(AppRadius.card)
```

### 4. String / Teks
```
❌ SALAH:  Text('Login')
✅ BENAR:  Text(AppStrings.login)
```
Untuk teks yang fix di UI, taruh di `app_strings.dart`. Untuk teks dari API, langsung pakai.

### 5. Navigasi
```
❌ SALAH:  Navigator.push(context, ...)
✅ BENAR:  context.go('/home')
✅ BENAR:  context.push('/skill/$skillId')
```
Selalu pakai GoRouter. Semua route didefinisikan di `app_router.dart`.

### 6. Widget Baru
Sebelum bikin widget di dalam halaman, tanya dulu:
- **Dipakai di ≥ 2 halaman?** → Taruh di `presentation/widgets/` (folder yang sesuai)
- **Hanya dipakai di 1 halaman?** → Taruh di `pages/<nama_halaman>/widgets/`

### 7. Halaman Baru
Setiap halaman baru HARUS punya folder sendiri:
```
pages/
  └── nama_halaman/
      ├── nama_halaman_page.dart     ← File utama halaman
      ├── bloc/                       ← BLoC/Cubit (jika bukan global, opsional)
      │   ├── nama_cubit.dart
      │   └── nama_state.dart
      └── widgets/                    ← Widget khusus halaman ini (opsional)
          └── komponen_spesifik.dart
```

### 8. API & Data
- **Model** (JSON ↔ Dart object): `data/models/`
- **API call**: `data/datasources/remote/`
- **Cache**: `data/datasources/local/`
- **Repository impl**: `data/repositories/`
- **Repository interface**: `domain/repositories/`
- **Business logic**: `domain/usecases/`
- **Pure entity**: `domain/entities/`

### 9. Error Handling
Setiap halaman **WAJIB** menangani 4 state:
1. **Loading** → Skeleton shimmer (`loading_shimmer.dart`), BUKAN spinner polos
2. **Empty** → Ilustrasi + pesan + CTA (`empty_state.dart`)
3. **Error** → Pesan error + tombol retry (`error_state.dart`)
4. **Offline** → Banner "Tidak ada koneksi" (`offline_banner.dart`)

### 10. Import Order
Urutkan import dalam kelompok, pisahkan dengan baris kosong:
```dart
// 1. Dart SDK
import 'dart:async';

// 2. Flutter framework
import 'package:flutter/material.dart';

// 3. Package pihak ketiga (alphabetical)
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

// 4. Package project (alphabetical) — barrel export untuk constants
import 'package:progressio_mobile/core/constants/constants.dart';
import 'package:progressio_mobile/domain/entities/user.dart';
```

---

## 🎨 Design System — Quick Reference

### Warna Utama

| Token | Hex | Penggunaan | File |
|---|---|---|---|
| `primary` | `#7CB8F2` | Tombol utama, link, accent | `app_colors.dart` |
| `primaryLight` | `#A8D4FF` | Secondary, highlight | `app_colors.dart` |
| `primaryDark` | `#5A9FE0` | Pressed state, emphasis | `app_colors.dart` |
| `background` | `#F5F8FC` | Background utama | `app_colors.dart` |
| `surface` | `#FFFFFF` | Card, dialog, bottom sheet | `app_colors.dart` |
| `textPrimary` | `#1E293B` | Headline, body text | `app_colors.dart` |
| `textSecondary` | `#64748B` | Caption, hint text | `app_colors.dart` |

### Warna Semantic

| Token | Hex | Penggunaan |
|---|---|---|
| `success` | `#81C995` | Jawaban benar, completed |
| `error` | `#E57373` | Jawaban salah, error state |
| `warning` | `#F2C97C` | Warning, streak about to end |

### Warna Gamifikasi

| Token | Hex | Penggunaan |
|---|---|---|
| `xpGold` | `#FFD700` | XP, reward, badge |
| `heartRed` | `#FF4757` | Hearts display |
| `streakOrange` | `#FF6B35` | Streak fire icon |
| `locked` | `#CBD5E1` | Locked skill/content |

### Typography

| Style | Font | Size | Weight |
|---|---|---|---|
| Headline | Plus Jakarta Sans | 28/24/22/20 | Bold/SemiBold |
| Body | Inter | 14/13 | Regular |
| Caption | Inter | 12/11 | Regular |
| Code | JetBrains Mono | 14 | Regular |
| Button | Plus Jakarta Sans | 16 | SemiBold |

### Spacing & Sizing

| Token | Value | Class |
|---|---|---|
| `xs` / `sm` / `md` / `lg` / `xl` / `xxl` / `xxxl` | 4 / 8 / 12 / 16 / 20 / 24 / 32 | `AppSpacing` |
| `screenPadding` | 16px horizontal | `AppSpacing` |
| `card` / `button` / `input` radius | 16 / 12 / 12 | `AppRadius` |
| Button height | 52px | `AppTheme` |

---

## 🗺️ Mapping Halaman → API Endpoint

### Endpoint yang Sudah Tersedia (Backend Existing)

| Halaman | API Endpoint |
|---|---|
| Login | `POST /api/v1/auth/login` |
| Register | `POST /api/v1/auth/register` |
| Token Refresh | `POST /api/v1/auth/refresh` |
| Home Dashboard | `GET /api/v1/auth/me` + `GET /api/v1/progress` |
| Career Tracks | `GET /api/v1/career-tracks` |
| Career Track Detail | `GET /api/v1/career-tracks/{id}` + `GET /api/v1/competencies?career_track={id}` |
| Learning Path | `GET /api/v1/learning-path?career_track={slug}` |
| Skill Detail | `GET /api/v1/skills/{id}` + `GET /api/v1/skills/{slug}/study-plan` |
| Lesson | `GET /api/v1/lessons/{id}` + `POST /api/v1/lesson/{id}/complete` |
| Checkpoint | `POST /api/v1/study-steps/{id}/checkpoint` |
| Assessment | `GET /api/v1/assessments/{id}` + `POST /api/v1/assessments/{id}/submit` |
| Diagnostic | `GET /api/v1/diagnostics/{id}` + `POST /api/v1/diagnostics/{id}/submit` |
| Diagnostic Result | `GET /api/v1/diagnostics/latest?career_track={id}` |
| Credentials | `GET /api/v1/credentials` |
| Credential Detail | `GET /api/v1/credentials/{id}` |
| Verification | `GET /api/v1/verify/{credential_id}` |
| Roadmap | `GET /api/v1/roadmap?skill={slug}` |
| Health Check | `GET /api/v1/health/` |

### Endpoint yang Perlu Ditambahkan di Backend

| Halaman | API Endpoint | Prioritas |
|---|---|---|
| Forgot Password | `POST /api/v1/auth/password-reset` | Must Have |
| Google Sign-In | `POST /api/v1/auth/google` | Should Have |
| Interest Selector | `PUT /api/v1/user/interests` | Must Have |
| Daily Goal | `PUT /api/v1/user/daily-goal` | Must Have |
| Home (XP/Level) | `GET /api/v1/gamification/xp` | Must Have |
| Home (Streak) | `GET /api/v1/gamification/streak` | Must Have |
| Home (Hearts) | `GET /api/v1/gamification/hearts` | Must Have |
| Profile (Badges) | `GET /api/v1/gamification/badges` | Should Have |
| Daily Challenge | `GET /api/v1/daily-challenge` | Should Have |
| Daily Challenge | `POST /api/v1/daily-challenge/submit` | Should Have |
| Leaderboard | `GET /api/v1/leaderboard?period=weekly` | Should Have |
| Friends | `GET /api/v1/friends` | Could Have |
| Friends | `POST /api/v1/friends/add` | Could Have |
| Friends | `POST /api/v1/friends/accept` | Could Have |
| Notifications | `GET /api/v1/notifications` | Should Have |

---

## 🧭 Navigasi (GoRouter)

### Bottom Navigation Bar (5 Tab)

```
┌───────────┬───────────┬───────────┬──────────┬────────┐
│  🏠       │  📚       │  ⚔️       │  🏆      │  👤    │
│ Beranda   │ Belajar   │ Tantangan │Sertifikat│ Profil │
└───────────┴───────────┴───────────┴──────────┴────────┘
```

### Route Tree

```
/                            → Splash
/onboarding                  → Onboarding
/interest                    → Interest Selector
/auth/login                  → Login
/auth/register               → Register
/auth/forgot-password        → Forgot Password
/diagnostic/:trackId         → Diagnostic Test
/diagnostic-result/:trackId  → Diagnostic Result
/home                        → Home (tab: beranda)
/learn                       → Learning Path (tab: belajar)
/learn/:trackSlug            → Learning Path specific track
/skill/:skillId              → Skill Detail
/lesson/:lessonId            → Lesson
/assessment/:assessmentId    → Assessment
/assessment-result/:id       → Assessment Result
/challenge                   → Daily Challenge (tab: tantangan)
/leaderboard                 → Leaderboard
/friends                     → Friends
/credentials                 → Credentials (tab: sertifikat)
/credential/:id              → Credential Detail
/credential/:id/share        → Share Credential
/profile                     → Profile (tab: profil)
/settings                    → Settings
/roadmap                     → Roadmap
/notification                → Notifications
```

---

## 📦 Assets

```text
assets/
├── images/       ← Gambar (PNG, JPG, SVG) — onboarding, empty state, ilustrasi
├── icons/        ← Icon custom (SVG) — skill icons, badge icons
├── fonts/        ← Font files (.ttf) — Plus Jakarta Sans, Inter, JetBrains Mono
└── animations/   ← Lottie/Rive files — confetti, level up, streak fire, heart break
```

Daftarkan di `pubspec.yaml` sebelum dipakai.

---

## 📦 Package Dependencies

| Package | Kegunaan |
|---|---|
| `flutter_bloc` | State management (BLoC + Cubit) |
| `go_router` | Declarative routing |
| `dio` | HTTP client |
| `get_it` + `injectable` | Dependency injection |
| `flutter_secure_storage` | Simpan JWT token |
| `shared_preferences` | Simpan settings & cache flag |
| `cached_network_image` | Image caching |
| `shimmer` | Skeleton loading effect |
| `lottie` | Animasi level up, confetti |
| `rive` | Animasi interaktif (streak fire, hearts) |
| `flutter_svg` | SVG icon rendering |
| `google_fonts` | Plus Jakarta Sans, Inter, JetBrains Mono |
| `flutter_markdown` | Render konten lesson |
| `flutter_highlight` | Syntax highlighting kode |
| `qr_flutter` | QR code sertifikat |
| `share_plus` | Share ke social media |
| `url_launcher` | Buka link eksternal |
| `connectivity_plus` | Deteksi status koneksi |
| `firebase_messaging` | Push notification |
| `flutter_local_notifications` | Notifikasi lokal (streak reminder) |
| `percent_indicator` | Circular & linear progress |
| `confetti` | Animasi confetti |
| `intl` | Format tanggal Bahasa Indonesia |

---

## 🚀 Cara Menjalankan

```bash
cd Mobile
flutter pub get
flutter run

# Analisa kode
flutter analyze

# Format kode
dart format lib/

# Test
flutter test

# Generate kode (jika pakai build_runner)
dart run build_runner build --delete-conflicting-outputs
```

---

## ✅ Checklist Sebelum Bikin Fitur Baru

1. [ ] Apakah folder halaman sudah ada? Kalau belum, buat dulu
2. [ ] Apakah warna/font/spacing sudah ada di constants? Kalau belum, tambahkan
3. [ ] Apakah widget ini reusable? Kalau ya, taruh di `widgets/`
4. [ ] Apakah model JSON sudah ada? Kalau belum, buat di `data/models/`
5. [ ] Apakah entity sudah ada? Kalau belum, buat di `domain/entities/`
6. [ ] Apakah endpoint sudah ada di `api_constants.dart`? Kalau belum, tambahkan
7. [ ] Apakah BLoC/Cubit sudah ada? Global → `blocs/`, per-halaman → `pages/<nama>/bloc/`
8. [ ] Apakah UseCase sudah ada? Kalau belum, buat di `domain/usecases/`
9. [ ] Apakah route sudah terdaftar di `app_router.dart`?
10. [ ] Apakah halaman sudah handle: loading (shimmer), empty, error, offline?
11. [ ] Apakah ada hardcode warna/font/spacing/string? Kalau ada, pindahkan ke constants
12. [ ] Apakah navigasi pakai GoRouter? Jangan pakai `Navigator.push()`
