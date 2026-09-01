# 📁 Progressio Mobile — Panduan Arsitektur & Struktur Folder

> **Aturan Utama:** Jangan pernah naruh file sembarangan. Setiap file HARUS masuk ke folder yang benar sesuai panduan ini. Kalau foldernya belum ada, **buat dulu** foldernya, baru buat filenya.

---

## 🏗️ Arsitektur: Clean Architecture (3 Layer)

```
┌──────────────────────────────────────────────────────┐
│                   PRESENTATION                        │
│         (UI, Widget, Page, State)                     │
├──────────────────────────────────────────────────────┤
│                      DOMAIN                           │
│      (Entity, UseCase, Repository Interface)          │
├──────────────────────────────────────────────────────┤
│                       DATA                            │
│   (Model, Repository Impl, DataSource, API)           │
└──────────────────────────────────────────────────────┘
```

Aliran data: **Page → UseCase → Repository → DataSource → API/Local**

---

## 📂 Struktur Folder Lengkap

```text
lib/
├── main.dart                          ← Entry point, JANGAN taruh logic di sini
├── app/
│   └── app.dart                       ← MaterialApp root widget
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
│   │   └── api_constants.dart         ← URL endpoint backend
│   │
│   ├── theme/                         ← ThemeData Flutter
│   │   └── app_theme.dart             ← SATU-SATUNYA tempat definisi theme
│   │
│   ├── network/                       ← HTTP client, interceptor, dio setup
│   │   └── (contoh: api_client.dart, dio_interceptor.dart)
│   │
│   ├── storage/                       ← Local storage (SharedPrefs, SecureStorage)
│   │   └── (contoh: local_storage.dart, secure_storage.dart)
│   │
│   ├── utils/                         ← Helper/utility function
│   │   └── (contoh: date_formatter.dart, validators.dart)
│   │
│   └── errors/                        ← Custom exception & failure classes
│       └── (contoh: app_exception.dart, failure.dart)
│
├── data/                              ← IMPLEMENTASI akses data
│   ├── models/                        ← Model JSON (fromJson/toJson)
│   │   └── (contoh: user_model.dart, career_track_model.dart)
│   │
│   ├── repositories/                  ← Implementasi repository (memanggil datasource)
│   │   └── (contoh: auth_repository_impl.dart)
│   │
│   └── datasources/
│       ├── remote/                    ← Panggilan API ke backend Django
│       │   └── (contoh: auth_remote_datasource.dart)
│       └── local/                     ← Cache lokal / offline data
│           └── (contoh: auth_local_datasource.dart)
│
├── domain/                            ← KONTRAK bisnis (tidak boleh import Flutter)
│   ├── entities/                      ← Object bisnis murni (bukan model JSON)
│   │   └── (contoh: user.dart, skill.dart)
│   │
│   ├── repositories/                  ← Abstract class / interface repository
│   │   └── (contoh: auth_repository.dart)
│   │
│   └── usecases/                      ← Satu class = satu aksi bisnis
│       └── (contoh: login_usecase.dart, get_career_tracks_usecase.dart)
│
└── presentation/                      ← SEMUA yang berhubungan dengan UI
    ├── widgets/                       ← Widget REUSABLE yang dipakai di banyak halaman
    │   ├── common/                    ← Widget umum (AppBar custom, loading, empty state)
    │   ├── buttons/                   ← Tombol-tombol custom
    │   ├── cards/                     ← Card custom (skill card, credential card, dll)
    │   ├── inputs/                    ← Text field custom, search bar, dll
    │   ├── dialogs/                   ← Dialog, bottom sheet, snackbar custom
    │   └── indicators/               ← Progress bar, circular ring, badge
    │
    ├── navigation/                    ← Router, bottom nav, route constants
    │   └── (contoh: app_router.dart, bottom_nav_shell.dart)
    │
    └── pages/                         ← SETIAP halaman punya folder sendiri
        ├── splash/
        │   └── splash_page.dart
        ├── onboarding/
        │   └── onboarding_page.dart
        ├── auth/
        │   ├── login/
        │   │   ├── login_page.dart
        │   │   └── widgets/           ← Widget yang HANYA dipakai di login
        │   │       └── login_form.dart
        │   └── register/
        │       ├── register_page.dart
        │       └── widgets/
        │           └── role_selector.dart
        ├── home/
        │   ├── home_page.dart
        │   └── widgets/
        │       ├── stats_row.dart
        │       └── current_track_card.dart
        ├── career_tracks/
        │   └── career_tracks_page.dart
        ├── career_track_detail/
        │   └── career_track_detail_page.dart
        ├── learning_path/
        │   └── learning_path_page.dart
        ├── skill_detail/
        │   └── skill_detail_page.dart
        ├── assessment/
        │   ├── assessment_page.dart
        │   └── widgets/
        │       └── answer_option_card.dart
        ├── assessment_result/
        │   └── assessment_result_page.dart
        ├── diagnostic/
        │   └── diagnostic_page.dart
        ├── credentials/
        │   └── credentials_page.dart
        ├── credential_detail/
        │   └── credential_detail_page.dart
        ├── verification/
        │   └── verification_page.dart
        ├── roadmap/
        │   └── roadmap_page.dart
        └── profile/
            └── profile_page.dart
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

### 3. Spacing & Radius
```
❌ SALAH:  padding: EdgeInsets.all(16)
✅ BENAR:  padding: EdgeInsets.all(AppSpacing.lg)
```

### 4. String / Teks
```
❌ SALAH:  Text('Login')
✅ BENAR:  Text(AppStrings.login)
```
Untuk teks yang fix di UI, taruh di `app_strings.dart`. Untuk teks dari API, langsung pakai.

### 5. Widget Baru
Sebelum bikin widget di dalam halaman, tanya dulu:
- **Dipakai di ≥ 2 halaman?** → Taruh di `presentation/widgets/` (folder yang sesuai)
- **Hanya dipakai di 1 halaman?** → Taruh di `pages/<nama_halaman>/widgets/`

### 6. Halaman Baru
Setiap halaman baru HARUS punya folder sendiri:
```
pages/
  └── nama_halaman/
      ├── nama_halaman_page.dart     ← File utama halaman
      └── widgets/                    ← Widget khusus halaman ini (opsional)
          └── komponen_spesifik.dart
```

### 7. API & Data
- **Model** (JSON ↔ Dart object): `data/models/`
- **API call**: `data/datasources/remote/`
- **Cache**: `data/datasources/local/`
- **Repository impl**: `data/repositories/`
- **Repository interface**: `domain/repositories/`
- **Business logic**: `domain/usecases/`
- **Pure entity**: `domain/entities/`

---

## 🎨 Design System — Quick Reference

| Token | Value | File |
|---|---|---|
| Primary Color | `#7CB8F2` (soft sky blue) | `app_colors.dart` |
| Secondary Color | `#A8D4FF` (pastel blue) | `app_colors.dart` |
| Background | `#F5F8FC` (ice gray) | `app_colors.dart` |
| Headline Font | Plus Jakarta Sans | `app_typography.dart` |
| Body Font | Inter | `app_typography.dart` |
| Card Radius | 16px | `app_spacing.dart` |
| Button Radius | 12px | `app_spacing.dart` |
| Button Height | 52px | `app_theme.dart` |
| Screen Padding | 16px horizontal | `app_spacing.dart` |

---

## 🗺️ Mapping Halaman → API Endpoint

| Halaman | API Endpoint |
|---|---|
| Login | `POST /api/v1/auth/login` |
| Register | `POST /api/v1/auth/register` |
| Home Dashboard | `GET /auth/me` + `GET /progress` |
| Career Tracks | `GET /career-tracks` |
| Career Track Detail | `GET /career-tracks/{id}` + `GET /competencies?career_track={id}` |
| Learning Path | `GET /learning-path?career_track={slug}` |
| Skill Detail | `GET /skills/{id}` + `GET /skills/{slug}/study-plan` |
| Assessment | `GET /assessments/{id}` + `POST /assessments/{id}/submit` |
| Diagnostic | `GET /diagnostics/{id}` + `POST /diagnostics/{id}/submit` |
| Credentials | `GET /credentials` |
| Credential Detail | `GET /credentials/{id}` |
| Verification | `GET /verify/{credential_id}` |
| Roadmap | `GET /roadmap?skill={slug}` |

---

## 📦 Assets

```text
assets/
├── images/     ← Gambar (PNG, JPG, SVG)
├── icons/      ← Icon custom (SVG)
└── fonts/      ← Font files (.ttf)
```

Daftarkan di `pubspec.yaml` sebelum dipakai.

---

## 🚀 Cara Menjalankan

```bash
cd Mobile
flutter pub get
flutter run
```

---

## ✅ Checklist Sebelum Bikin Fitur Baru

1. [ ] Apakah folder halaman sudah ada? Kalau belum, buat dulu
2. [ ] Apakah warna/font/spacing sudah ada di constants? Kalau belum, tambahkan
3. [ ] Apakah widget ini reusable? Kalau ya, taruh di `widgets/`
4. [ ] Apakah model JSON sudah ada? Kalau belum, buat di `data/models/`
5. [ ] Apakah endpoint sudah ada di `api_constants.dart`? Kalau belum, tambahkan
