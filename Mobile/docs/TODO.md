# 📋 TODO — Progressio Mobile

> **File ini adalah "memori" project.** Update setiap kali ada perubahan.  
> Status: `✅` Selesai · `🔄` Sedang dikerjakan · `⬜` Belum mulai  
> Terakhir diupdate: **2 September 2026**

---

## Status Codebase Saat Ini

**Yang SUDAH ada (berisi kode):**
- `main.dart`, `app/app.dart`, `splash/splash_page.dart`
- `core/constants/` — 6 file lengkap (colors, typography, spacing, strings, api, barrel)
- `core/theme/app_theme.dart`

**Yang SUDAH ada (folder kosong, belum ada kode):**
- `core/` — network, storage, utils, errors
- `data/` — models, repositories, datasources (remote + local)
- `domain/` — entities, repositories, usecases
- `presentation/widgets/` — 6 subfolder (buttons, cards, common, dialogs, indicators, inputs)
- `presentation/navigation/`
- `presentation/pages/` — 15 folder halaman (tanpa file dart, hanya splash yang ada)

**Yang BELUM ada (folder belum dibuat):**
- `presentation/blocs/` (global BLoC/Cubit)
- `presentation/widgets/gamification/`
- Halaman baru: interest_selector, forgot_password, lesson, diagnostic_result, daily_challenge, leaderboard, friends, share_credential, settings, notification
- `core/constants/gamification_constants.dart`

---

## Sprint 1 — Foundation & Auth

| # | Task | Status | Catatan |
|---|---|---|---|
| 1.1 | Setup BLoC + GoRouter + Dio + get_it di `pubspec.yaml` | ⬜ | |
| 1.2 | `core/network/` — api_client, dio_interceptor, token_interceptor | ⬜ | |
| 1.3 | `core/storage/` — local_storage, secure_storage | ⬜ | |
| 1.4 | `core/errors/` — failure.dart, app_exception.dart | ⬜ | |
| 1.5 | `core/constants/gamification_constants.dart` | ⬜ | XP values, level thresholds |
| 1.6 | Update `app.dart` — MultiBlocProvider + GoRouter | ⬜ | Ganti MaterialApp → MaterialApp.router |
| 1.7 | `presentation/navigation/` — app_router, bottom_nav_shell | ⬜ | 5 tab: Beranda, Belajar, Tantangan, Sertifikat, Profil |
| 1.8 | `presentation/blocs/auth/` — AuthBloc global | ⬜ | |
| 1.9 | `presentation/blocs/user/` — UserCubit global | ⬜ | |
| 1.10 | Domain + Data layer Auth — entity, model, repo, usecase, datasource | ⬜ | |
| 1.11 | Splash Page | ✅ | Sudah ada, perlu update logic cek JWT |
| 1.12 | Onboarding Page (3 slides) | ⬜ | Folder ada, belum ada dart file |
| 1.13 | Interest Selector Page | ⬜ | Folder belum ada |
| 1.14 | Register Page + form validation | ⬜ | Folder ada |
| 1.15 | Login Page + JWT token management | ⬜ | Folder ada |
| 1.16 | Forgot Password Page | ⬜ | Folder belum ada |
| 1.17 | Home Dashboard (layout + widget) | ⬜ | Folder ada |
| 1.18 | Widget reusable: loading_shimmer, empty_state, error_state, offline_banner | ⬜ | |

## Sprint 2 — Learning Engine

| # | Task | Status | Catatan |
|---|---|---|---|
| 2.1 | Domain + Data layer Learning — entity, model, repo, usecase, datasource | ⬜ | career_track, competency, skill, lesson |
| 2.2 | Career Tracks Page | ⬜ | Folder ada |
| 2.3 | Career Track Detail Page | ⬜ | Folder ada |
| 2.4 | Diagnostic Test Page + BLoC | ⬜ | Folder ada |
| 2.5 | Diagnostic Result Page | ⬜ | Folder belum ada |
| 2.6 | Learning Path Page (skill graph visual) + BLoC | ⬜ | Folder ada |
| 2.7 | Skill Detail Page + study plan | ⬜ | Folder ada |
| 2.8 | Lesson Page + BLoC + 5 tipe soal widget | ⬜ | Folder belum ada, widget: multiple_choice, fill_in_blank, arrange_code, true_false, match_pairs |
| 2.9 | Assessment Page + BLoC | ⬜ | Folder ada |
| 2.10 | Assessment Result Page | ⬜ | Folder ada |
| 2.11 | Roadmap Page | ⬜ | Folder ada |

## Sprint 3 — Gamification

| # | Task | Status | Catatan |
|---|---|---|---|
| 3.1 | `presentation/blocs/gamification/` — GamificationCubit global | ⬜ | XP, level, streak, hearts, daily goal |
| 3.2 | Widget: xp_bar, hearts_display, streak_counter, mastery_ring, level_badge | ⬜ | `widgets/indicators/` |
| 3.3 | Widget: confetti_overlay, level_up_overlay, xp_float_animation, heart_break | ⬜ | `widgets/gamification/` — folder belum ada |
| 3.4 | Hearts system (display, deduct, regen timer) | ⬜ | |
| 3.5 | Streak system (counter, milestone, reset) | ⬜ | |
| 3.6 | Daily Goal (selector, progress ring) | ⬜ | |
| 3.7 | Daily Challenge Page + BLoC | ⬜ | Folder belum ada |
| 3.8 | Badge system (collection, unlock) | ⬜ | |

## Sprint 4 — Social & Credential

| # | Task | Status | Catatan |
|---|---|---|---|
| 4.1 | Leaderboard Page | ⬜ | Folder belum ada |
| 4.2 | Friends Page | ⬜ | Folder belum ada |
| 4.3 | Credentials Page | ⬜ | Folder ada |
| 4.4 | Credential Detail Page (certificate preview, QR, blockchain) | ⬜ | Folder ada |
| 4.5 | Share Credential Page | ⬜ | Folder belum ada |
| 4.6 | Profile Page (stats, badges, heatmap) | ⬜ | Folder ada |
| 4.7 | Settings Page | ⬜ | Folder belum ada |
| 4.8 | Notification Page + Cubit global | ⬜ | Folder belum ada |
| 4.9 | Push notification integration (Firebase) | ⬜ | |

## Sprint 5 — Polish & QA

| # | Task | Status | Catatan |
|---|---|---|---|
| 5.1 | Offline caching (lesson cache) | ⬜ | |
| 5.2 | Error handling & edge cases semua halaman | ⬜ | |
| 5.3 | Skeleton shimmer di semua halaman | ⬜ | |
| 5.4 | Animasi polish (page transition, micro-interaction) | ⬜ | |
| 5.5 | Unit test domain layer (UseCase) | ⬜ | |
| 5.6 | Unit test data layer (Model fromJson/toJson) | ⬜ | |
| 5.7 | Widget test halaman utama | ⬜ | |
| 5.8 | Performance optimization | ⬜ | |

---

## Log Perubahan

| Tanggal | Apa yang Berubah | Oleh |
|---|---|---|
| 2 Sep 2026 | Setup awal: main.dart, app.dart, splash_page, constants (6 file), theme | AI |
| 2 Sep 2026 | Buat PRD_MOBILE.md, AGENTS.md, update ARCHITECTURE.md | AI |
| | | |
