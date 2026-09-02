# 🤖 AGENTS.md — Instruksi AI untuk Progressio Mobile

> **Terakhir diperbarui:** 2 September 2026  
> **Scope:** Khusus codebase Flutter di folder `Mobile/`  
> **Tujuan:** Memastikan setiap AI assistant yang bekerja di repo ini menghasilkan kode yang konsisten, bersih, dan sesuai arsitektur yang sudah ditetapkan.

---

## 1. Konteks Project

**Progressio Mobile** adalah aplikasi mobile pembelajaran coding bergaya Duolingo, dibangun dengan **Flutter (Dart)**. Aplikasi ini berkomunikasi dengan backend Django REST API.

### Dokumen Wajib Baca

Sebelum menulis kode apa pun, **WAJIB** baca dokumen-dokumen ini:

| Dokumen | Path | Isi |
|---|---|---|
| Arsitektur & Struktur Folder | `docs/ARCHITECTURE.md` | Clean Architecture 3 layer, aturan penempatan file, design system |
| PRD Mobile | `docs/PRD_MOBILE.md` | Spesifikasi fitur, halaman, gamifikasi, API mapping |
| Platform Native | `docs/NATIVE_PLATFORMS.md` | Kapan dan bagaimana menyentuh folder `android/` dan `ios/` |
| Backend Spec | `../progressio-backend-spec.md` | API endpoints, domain model, flow backend |

### Stack Teknologi

| Aspek | Pilihan |
|---|---|
| Framework | Flutter — Dart SDK ^3.11.0 |
| Arsitektur | Clean Architecture (Presentation → Domain → Data) |
| State Management | BLoC / Cubit (`flutter_bloc`) |
| Navigasi | GoRouter (`go_router`) |
| HTTP Client | Dio (`dio`) |
| DI | get_it + injectable |
| Local Storage | SharedPreferences + flutter_secure_storage |
| Linting | `flutter_lints` (lihat `analysis_options.yaml`) |

---

## 2. Arsitektur — Aturan Mutlak

### 2.1 Tiga Layer (Tidak Boleh Dilanggar)

```
PRESENTATION  →  Hanya tahu UI. Tidak boleh import dari data/.
DOMAIN        →  Bisnis murni. Tidak boleh import Flutter atau package luar.
DATA          →  Implementasi akses data. Boleh import domain/, tidak boleh import presentation/.
```

**Aliran dependensi:**
```
presentation/ → domain/ → (tidak import apa-apa selain Dart core)
presentation/ → TIDAK BOLEH import data/
data/         → domain/ (implement interface repository)
data/         → TIDAK BOLEH import presentation/
```

### 2.2 Penempatan File

| Jenis File | Lokasi | Contoh |
|---|---|---|
| Entity (object bisnis murni) | `lib/domain/entities/` | `user.dart`, `skill.dart` |
| Repository interface | `lib/domain/repositories/` | `auth_repository.dart` |
| UseCase | `lib/domain/usecases/` | `login_usecase.dart` |
| Model JSON (fromJson/toJson) | `lib/data/models/` | `user_model.dart` |
| Repository implementation | `lib/data/repositories/` | `auth_repository_impl.dart` |
| Remote data source (API) | `lib/data/datasources/remote/` | `auth_remote_datasource.dart` |
| Local data source (cache) | `lib/data/datasources/local/` | `auth_local_datasource.dart` |
| Halaman/screen | `lib/presentation/pages/<nama>/` | `home/home_page.dart` |
| Widget khusus halaman | `lib/presentation/pages/<nama>/widgets/` | `home/widgets/stats_row.dart` |
| Widget reusable (≥2 halaman) | `lib/presentation/widgets/<kategori>/` | `widgets/cards/skill_card.dart` |
| BLoC/Cubit global | `lib/presentation/blocs/<nama>/` | `blocs/auth/auth_bloc.dart` |
| BLoC/Cubit per-halaman | `lib/presentation/pages/<nama>/bloc/` | `home/bloc/home_cubit.dart` |
| Konstanta | `lib/core/constants/` | `app_colors.dart` |
| Theme | `lib/core/theme/` | `app_theme.dart` |
| Network/HTTP | `lib/core/network/` | `api_client.dart` |
| Error class | `lib/core/errors/` | `app_exception.dart` |
| Utility | `lib/core/utils/` | `date_formatter.dart` |

### 2.3 Aturan Halaman Baru

Setiap halaman baru **WAJIB** punya folder sendiri:

```
pages/
  └── nama_halaman/
      ├── nama_halaman_page.dart       ← File utama
      ├── bloc/                         ← BLoC/Cubit (jika bukan global)
      │   ├── nama_cubit.dart
      │   └── nama_state.dart
      └── widgets/                      ← Widget khusus halaman ini
          └── komponen_spesifik.dart
```

**Jangan pernah** menaruh file halaman langsung di `pages/` tanpa subfolder.

---

## 3. Coding Style & Konvensi

### 3.1 Penamaan

| Jenis | Konvensi | Contoh |
|---|---|---|
| File | `snake_case.dart` | `career_track_card.dart` |
| Class | `PascalCase` | `CareerTrackCard` |
| Variable & function | `camelCase` | `careerTrackList` |
| Konstanta | `camelCase` (dalam class) | `AppColors.primary` |
| Enum | `PascalCase` (nama), `camelCase` (value) | `AssessmentType.quiz` |
| BLoC Event | `PascalCase` + deskriptif | `LoginRequested`, `AssessmentSubmitted` |
| BLoC State | `PascalCase` + status | `AuthInitial`, `AuthLoading`, `AuthSuccess`, `AuthFailure` |
| Private member | `_camelCase` | `_isLoading` |

### 3.2 Penamaan Suffix

| Jenis | Suffix | Contoh |
|---|---|---|
| Halaman | `Page` | `HomePage`, `LoginPage` |
| Widget | Deskriptif (tanpa suffix khusus) | `StatsRow`, `SkillCard` |
| Model (JSON) | `Model` | `UserModel`, `SkillModel` |
| Entity | Tanpa suffix | `User`, `Skill` |
| Repository interface | `Repository` | `AuthRepository` |
| Repository impl | `RepositoryImpl` | `AuthRepositoryImpl` |
| UseCase | `UseCase` | `LoginUseCase` |
| Remote datasource | `RemoteDataSource` | `AuthRemoteDataSource` |
| Local datasource | `LocalDataSource` | `AuthLocalDataSource` |
| BLoC | `Bloc` | `AuthBloc` |
| Cubit | `Cubit` | `HomeCubit` |
| State | `State` | `HomeState` |
| Event | Deskriptif (verb) | `LoginRequested` |

### 3.3 Format Docstring & Komentar

Gunakan format docstring dengan garis separator yang sudah dipakai di codebase:

```dart
/// ─────────────────────────────────────────────────────────────────────────────
/// NamaClass — Deskripsi singkat
/// ─────────────────────────────────────────────────────────────────────────────
/// Penjelasan tambahan jika diperlukan.
/// ─────────────────────────────────────────────────────────────────────────────
class NamaClass {
```

Untuk section di dalam class, gunakan komentar inline:

```dart
  // ── Section Name ────────────────────────────────────────────────────────
  static const Color primary = Color(0xFF7CB8F2);
```

**Aturan komentar:**
- Selalu pakai `///` untuk doc comment pada class, method publik, dan konstanta penting.
- Pakai `//` untuk komentar inline/implementasi.
- Gunakan `// ── Section ──...` untuk pemisah section dalam file panjang.
- **Jangan** hapus komentar/docstring yang sudah ada kecuali diminta secara eksplisit.
- Tulis komentar dalam **Bahasa Indonesia** untuk konsistensi dengan dokumentasi project.

### 3.4 Import Order

Urutkan import dalam kelompok berikut, pisahkan dengan baris kosong:

```dart
// 1. Dart SDK
import 'dart:async';
import 'dart:convert';

// 2. Flutter framework
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// 3. Package pihak ketiga (alphabetical)
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

// 4. Package project (alphabetical)
import 'package:progressio_mobile/core/constants/constants.dart';
import 'package:progressio_mobile/domain/entities/user.dart';
```

### 3.5 Class Structure

Urutan member di dalam class widget:

```dart
class MyPage extends StatelessWidget {
  // 1. Constructor
  const MyPage({super.key});

  // 2. Static/const members
  static const String routeName = '/my-page';

  // 3. Final fields
  final String title;

  // 4. build method (untuk widget)
  @override
  Widget build(BuildContext context) { ... }

  // 5. Private helper methods
  Widget _buildHeader() { ... }
}
```

---

## 4. Design System — Aturan Wajib

### 4.1 DILARANG KERAS (Hard Rules)

```
❌ DILARANG: Color(0xFF7CB8F2)          → Hardcode warna
✅ WAJIB:    AppColors.primary           → Dari constants

❌ DILARANG: fontSize: 16               → Hardcode font size
✅ WAJIB:    fontSize: AppTypography.subtitle1  → Dari constants

❌ DILARANG: padding: EdgeInsets.all(16) → Hardcode spacing
✅ WAJIB:    padding: EdgeInsets.all(AppSpacing.lg)  → Dari constants

❌ DILARANG: BorderRadius.circular(16)  → Hardcode radius
✅ WAJIB:    BorderRadius.circular(AppRadius.card)   → Dari constants

❌ DILARANG: Text('Login')              → Hardcode string UI
✅ WAJIB:    Text(AppStrings.login)      → Dari constants

❌ DILARANG: TextStyle(color: Colors.black, fontSize: 20)
✅ WAJIB:    Theme.of(context).textTheme.titleLarge
```

### 4.2 Sumber Kebenaran Design System

| Apa | File | Class |
|---|---|---|
| Semua warna | `lib/core/constants/app_colors.dart` | `AppColors` |
| Font size & family | `lib/core/constants/app_typography.dart` | `AppTypography` |
| Spacing & padding | `lib/core/constants/app_spacing.dart` | `AppSpacing`, `AppRadius` |
| Teks UI statis | `lib/core/constants/app_strings.dart` | `AppStrings` |
| API endpoint | `lib/core/constants/api_constants.dart` | `ApiConstants` |
| ThemeData | `lib/core/theme/app_theme.dart` | `AppTheme` |

### 4.3 Barrel Export

Selalu import constants melalui barrel file:

```dart
// ✅ BENAR — satu import untuk semua constants
import 'package:progressio_mobile/core/constants/constants.dart';

// ❌ SALAH — import file individual (kecuali hanya butuh satu)
import 'package:progressio_mobile/core/constants/app_colors.dart';
import 'package:progressio_mobile/core/constants/app_spacing.dart';
```

### 4.4 Menambah Token Baru

Jika butuh warna/spacing/string baru:
1. **Cek dulu** apakah token serupa sudah ada.
2. Jika belum ada, **tambahkan di file constants yang sesuai** — bukan hardcode di widget.
3. Ikuti naming convention dan section separator yang sudah ada.
4. Pastikan barrel export di `constants.dart` sudah mencakup file baru (jika membuat file constants baru).

---

## 5. Widget — Aturan Pembuatan

### 5.1 Kapan Widget Jadi Reusable vs Lokal

| Pertanyaan | Jawaban | Taruh di |
|---|---|---|
| Dipakai di ≥ 2 halaman? | Ya | `presentation/widgets/<kategori>/` |
| Hanya dipakai di 1 halaman? | Ya | `presentation/pages/<nama>/widgets/` |

**Kategori widget reusable yang tersedia:**
- `widgets/common/` — AppBar custom, loading, empty state, error state
- `widgets/buttons/` — Tombol custom
- `widgets/cards/` — Card custom (skill card, credential card, dll)
- `widgets/inputs/` — Text field custom, search bar
- `widgets/dialogs/` — Dialog, bottom sheet, snackbar
- `widgets/indicators/` — Progress bar, circular ring, badge
- `widgets/gamification/` — Animasi XP, confetti, level up

### 5.2 Konstruktor Widget

Selalu gunakan `const` constructor jika memungkinkan:

```dart
class SkillCard extends StatelessWidget {
  const SkillCard({
    super.key,
    required this.skill,
    this.onTap,
  });

  final Skill skill;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) { ... }
}
```

### 5.3 Responsive Layout

- Gunakan `MediaQuery.sizeOf(context)` (bukan `MediaQuery.of(context).size`) untuk performa.
- Screen padding horizontal selalu `AppSpacing.screenPadding` (16px).
- Gunakan `LayoutBuilder` untuk widget yang perlu adaptif.
- Jangan hardcode width/height — biarkan Flutter layout system bekerja.

---

## 6. State Management (BLoC/Cubit)

### 6.1 Kapan Pakai BLoC vs Cubit

| Gunakan | Kapan |
|---|---|
| **Cubit** | State sederhana, tidak perlu event terpisah (contoh: `HomeCubit`, `SettingsCubit`) |
| **BLoC** | State kompleks, event-driven, butuh transformasi event (contoh: `AuthBloc`, `AssessmentBloc`) |

### 6.2 Pola State dengan Freezed atau Sealed Class

```dart
// State untuk Cubit sederhana
sealed class HomeState {}
class HomeInitial extends HomeState {}
class HomeLoading extends HomeState {}
class HomeLoaded extends HomeState {
  final UserProfile user;
  final List<CareerTrack> recommendedTracks;
  HomeLoaded({required this.user, required this.recommendedTracks});
}
class HomeError extends HomeState {
  final String message;
  HomeError(this.message);
}
```

### 6.3 Scope BLoC/Cubit

| Scope | Ditempatkan di | Contoh |
|---|---|---|
| **Global** (selalu tersedia) | `app.dart` via `MultiBlocProvider` | `AuthBloc`, `GamificationCubit` |
| **Per-halaman** (disposable) | `BlocProvider` di dalam page route | `LessonCubit`, `AssessmentBloc` |

### 6.4 Jangan Lakukan

```dart
// ❌ JANGAN panggil API langsung dari BLoC/Cubit
class HomeCubit extends Cubit<HomeState> {
  Future<void> load() async {
    final response = await Dio().get('/api/v1/career-tracks');  // SALAH!
  }
}

// ✅ BENAR — panggil melalui UseCase
class HomeCubit extends Cubit<HomeState> {
  final GetCareerTracksUseCase _getCareerTracks;
  
  Future<void> load() async {
    emit(HomeLoading());
    final result = await _getCareerTracks();
    // ...
  }
}
```

---

## 7. Data Layer — Aturan

### 7.1 Model vs Entity

| | Entity (`domain/entities/`) | Model (`data/models/`) |
|---|---|---|
| Tujuan | Object bisnis murni | Serialisasi JSON |
| Dependency | Dart core saja | Boleh import entity |
| Contoh method | Business logic | `fromJson()`, `toJson()` |
| Dipakai oleh | UseCase, Repository interface | DataSource, Repository impl |

```dart
// domain/entities/user.dart — MURNI, tidak tahu JSON
class User {
  final String id;
  final String name;
  final String email;
  final String role;
  
  const User({required this.id, required this.name, required this.email, required this.role});
}

// data/models/user_model.dart — TAHU JSON, extends/implement Entity
class UserModel extends User {
  const UserModel({required super.id, required super.name, required super.email, required super.role});
  
  factory UserModel.fromJson(Map<String, dynamic> json) => UserModel(
    id: json['id'] as String,
    name: json['name'] as String,
    email: json['email'] as String,
    role: json['role'] as String,
  );
  
  Map<String, dynamic> toJson() => {'id': id, 'name': name, 'email': email, 'role': role};
}
```

### 7.2 Repository Pattern

```dart
// domain/repositories/auth_repository.dart — INTERFACE
abstract class AuthRepository {
  Future<User> login(String email, String password);
  Future<User> register(String name, String email, String password);
  Future<void> logout();
}

// data/repositories/auth_repository_impl.dart — IMPLEMENTASI
class AuthRepositoryImpl implements AuthRepository {
  final AuthRemoteDataSource _remoteDataSource;
  final AuthLocalDataSource _localDataSource;
  
  AuthRepositoryImpl(this._remoteDataSource, this._localDataSource);
  
  @override
  Future<User> login(String email, String password) async {
    final model = await _remoteDataSource.login(email, password);
    await _localDataSource.cacheToken(model.token);
    return model;
  }
}
```

### 7.3 API Integration

- **Base URL:** `http://10.0.2.2:8000` (Android emulator → localhost)
- **API Version:** `/api/v1`
- Semua endpoint WAJIB didaftarkan di `lib/core/constants/api_constants.dart`
- Gunakan `Dio` untuk HTTP requests — jangan pakai `http` package langsung.
- Implementasi `token_interceptor` untuk auto-refresh JWT.

---

## 8. Navigasi

### 8.1 GoRouter

- Semua route didefinisikan di `lib/presentation/navigation/app_router.dart`.
- Setiap halaman WAJIB punya `static const String routePath`.
- Bottom navigation menggunakan `ShellRoute`.
- Deep link support harus dipertimbangkan dari awal.

### 8.2 Pattern Navigasi

```dart
// Navigasi menggunakan GoRouter
context.go('/home');              // Replace
context.push('/skill/$skillId');  // Push
context.pop();                    // Pop

// JANGAN pakai Navigator langsung
Navigator.push(context, ...);     // ❌ DILARANG
```

---

## 9. Error Handling

### 9.1 Pattern

Gunakan sealed class atau custom exception:

```dart
// core/errors/
sealed class Failure {
  final String message;
  const Failure(this.message);
}

class ServerFailure extends Failure {
  final int? statusCode;
  const ServerFailure(super.message, {this.statusCode});
}

class NetworkFailure extends Failure {
  const NetworkFailure(super.message);
}

class CacheFailure extends Failure {
  const CacheFailure(super.message);
}
```

### 9.2 Handling di UseCase/Repository

```dart
// Gunakan Either pattern atau try-catch yang terstruktur
// Jangan biarkan exception naik ke UI tanpa ditangkap

Future<User> login(String email, String password) async {
  try {
    return await _remoteDataSource.login(email, password);
  } on DioException catch (e) {
    throw ServerFailure(
      e.response?.data['message'] ?? 'Terjadi kesalahan pada server',
      statusCode: e.response?.statusCode,
    );
  } on SocketException {
    throw const NetworkFailure('Tidak ada koneksi internet');
  }
}
```

### 9.3 UI Error State

Setiap halaman WAJIB menangani:
1. **Loading** — skeleton shimmer, bukan spinner polos
2. **Empty** — ilustrasi + pesan + CTA
3. **Error** — pesan error + tombol retry
4. **Offline** — banner "Tidak ada koneksi"

---

## 10. Testing

### 10.1 Prioritas Test

| Prioritas | Layer | Test |
|---|---|---|
| 🔴 Tinggi | Domain | Unit test untuk setiap UseCase |
| 🔴 Tinggi | Data | Unit test untuk Model (fromJson/toJson) |
| 🟡 Sedang | Data | Unit test untuk Repository implementation |
| 🟡 Sedang | Presentation | Widget test untuk halaman utama |
| 🟢 Rendah | Presentation | Widget test untuk widget kecil |
| 🟢 Rendah | Integration | Flow test end-to-end |

### 10.2 Naming Convention Test

```dart
// File test: nama_file_test.dart (suffix _test)
// Group: deskripsi class/function
// Test: 'should [expected behavior] when [condition]'

void main() {
  group('LoginUseCase', () {
    test('should return User when login is successful', () async {
      // arrange
      // act
      // assert
    });

    test('should throw ServerFailure when credentials are invalid', () async {
      // arrange
      // act
      // assert
    });
  });
}
```

### 10.3 Menjalankan Test

```bash
cd Mobile
flutter test                          # Semua test
flutter test test/domain/             # Test domain layer saja
flutter test --coverage               # Dengan coverage report
```

---

## 11. Pola yang DILARANG

### 11.1 Anti-Pattern Checklist

| # | Yang Dilarang | Alasan |
|---|---|---|
| 1 | Hardcode warna (`Color(0xFF...)`) di widget | Pakai `AppColors` |
| 2 | Hardcode font size di widget | Pakai `AppTypography` atau `Theme.of(context).textTheme` |
| 3 | Hardcode spacing/padding di widget | Pakai `AppSpacing` / `AppRadius` |
| 4 | Hardcode string UI di widget | Pakai `AppStrings` |
| 5 | Hardcode URL API | Pakai `ApiConstants` |
| 6 | Import `data/` dari `presentation/` | Layer violation — pakai UseCase/BLoC |
| 7 | Import Flutter di `domain/` | Domain harus murni Dart |
| 8 | Panggil API langsung dari Widget/BLoC | Lewat UseCase → Repository → DataSource |
| 9 | `Navigator.push()` langsung | Pakai GoRouter: `context.go()` / `context.push()` |
| 10 | Logic di `main.dart` | `main.dart` hanya setup awal, logic di `app.dart` |
| 11 | `setState()` untuk state kompleks | Pakai BLoC/Cubit |
| 12 | File halaman tanpa subfolder di `pages/` | Setiap halaman HARUS punya folder sendiri |
| 13 | `print()` untuk debugging | Pakai `debugPrint()` atau logger package |
| 14 | Menyentuh `android/` atau `ios/` untuk logic/UI | Hanya untuk permission, icon, signing — lihat `docs/NATIVE_PLATFORMS.md` |
| 15 | Menghapus komentar/docstring yang sudah ada | Pertahankan kecuali diminta eksplisit |

---

## 12. Checklist Sebelum Submit Kode

Setiap kali menulis atau memodifikasi kode, pastikan:

- [ ] **Arsitektur:** File ada di layer dan folder yang benar
- [ ] **Naming:** Nama file `snake_case`, class `PascalCase`, suffix sesuai jenis
- [ ] **Design System:** Tidak ada hardcode warna/font/spacing/string — semua dari constants
- [ ] **Import:** Urutan import benar, pakai barrel export untuk constants
- [ ] **State:** Menggunakan BLoC/Cubit, bukan `setState` untuk state kompleks
- [ ] **Error:** Loading, empty, error, offline state tertangani
- [ ] **Komentar:** Doc comment pada class dan method publik, pakai format separator `──`
- [ ] **Const:** Widget menggunakan `const` constructor jika memungkinkan
- [ ] **Test:** Ada unit test untuk UseCase dan Model baru
- [ ] **Tidak melanggar:** Tidak ada item di daftar "Anti-Pattern" yang dilanggar

---

## 13. Perintah Berguna

```bash
# Menjalankan app
cd Mobile
flutter pub get
flutter run

# Analisa kode
flutter analyze

# Format kode
dart format lib/

# Test
flutter test

# Build APK
flutter build apk --release

# Build iOS (hanya di macOS)
flutter build ios --release

# Generate kode (jika pakai build_runner, injectable, freezed, dll)
dart run build_runner build --delete-conflicting-outputs
```

---

## 14. Catatan Tambahan untuk AI

### 14.1 Konteks Gamifikasi

Project ini memiliki sistem gamifikasi yang kompleks (XP, hearts, streak, level, badge, daily challenge, leaderboard). Saat mengerjakan fitur gamifikasi:
- Nilai XP dan threshold level didefinisikan di PRD (`docs/PRD_MOBILE.md` section 8).
- Hearts regenerasi 1 per 30 menit, full refill pukul 00:00 WIB.
- Streak bertambah jika user menyelesaikan minimal 1 lesson/challenge per hari.

### 14.2 Bahasa Konten

- **Seluruh UI** menggunakan Bahasa Indonesia.
- **Komentar kode** dalam Bahasa Indonesia.
- **Nama class, variable, function** dalam Bahasa Inggris.
- **Commit message** dalam Bahasa Inggris.

### 14.3 Ketika Ragu

1. **Cek `docs/ARCHITECTURE.md`** untuk aturan penempatan file.
2. **Cek `docs/PRD_MOBILE.md`** untuk spesifikasi fitur.
3. **Cek file constants** yang sudah ada sebelum membuat token baru.
4. **Cek kode yang sudah ada** untuk melihat pola yang sudah diterapkan.
5. **Tanya user** jika ada ambiguitas yang tidak bisa diselesaikan dari dokumentasi.

### 14.4 Prioritas saat Konflik

Jika ada konflik antara dokumen:
1. **Kode yang sudah ada** (source of truth tertinggi untuk pattern)
2. **`docs/ARCHITECTURE.md`** (aturan arsitektur)
3. **`docs/PRD_MOBILE.md`** (spesifikasi fitur)
4. **File AGENTS.md ini** (pedoman umum)
