# 🎨 DESIGN.md — Progressio Mobile Design System & UI/UX Specification

> **Version:** 1.0.0 (Dopamine Gamified Edition)  
> **Target Platform:** Mobile (Flutter — Android & iOS)  
> **Design Archetype:** *Neo-Dopamine Gamified UI* (High Contrast, Electric Accents, Modular Pill Geometry)  
> **Design Language Reference:** Duolingo-style gamified learning meets vibrant Dopamine visual aesthetics  
> **Tagline:** *Turning Progress Into Proof.*
>
> 📌 **PANDUAN UNTUK AI ASSISTANT / DEVELOPER:**
> 1. Setiap membuat atau merevisi halaman UI, **WAJIB** periksa folder `docs/design/figma_screens/` untuk melihat apakah ada screenshot mockup Figma untuk halaman tersebut.
> 2. Jika ada screenshot mockup di `docs/design/figma_screens/` atau komponen di `docs/design/components/`, **jadikan sebagai acuan visual 1:1** untuk struktur tata letak (layout), margin/padding, hierarki kartu, ikon, dan kombinasi warna.
> 3. Semua warna, font, dan spacing tetap **WAJIB** diambil dari `AppColors`, `AppTypography`, dan `AppSpacing` di `lib/core/constants/`.

---

## 📁 Struktur Folder Desain & Mockup Figma

```text
docs/design/
├── DESIGN.md                ← Dokumen spesifikasi token & panduan UI/UX (file ini)
├── figma_screens/           ← Tangkapan layar utuh screen dari Figma
└── components/              ← Tangkapan layar potongan widget / detail komponen
```

*Aturan penamaan file mockup di `figma_screens/`:*
Gunakan format snake_case sesuai nama halaman di `lib/presentation/pages/`, contoh:
- `01_splash_page.png`
- `02_onboarding_page.png`
- `03_interest_selector_page.png`
- `04_login_page.png`
- `05_home_page.png`
- `06_learning_path_page.png`
- `07_lesson_page.png`
- `08_assessment_page.png`
- `09_credential_detail_page.png`

---

## 1. Visi & Filosofi Desain

Progressio Mobile mengusung pendekatan **Dopamine Design Language** yang dipadukan secara harmonis dengan metodologi gamifikasi pembelajaran coding intensif. Konsep ini dirancang untuk mengatasi kelelahan kognitif (*cognitive fatigue*) saat mempelajari materi pemrograman yang abstrak, mengubah setiap pencapaian kecil menjadi umpan balik dopamin visual (*visual dopamine feedback loop*) yang memuaskan dan adiktif secara positif.

### 1.1 Tiga Pilar Visual Utama

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DOPAMINE DESIGN PILLARS                         │
├───────────────────┬──────────────────────────┬─────────────────────────┤
│ ⚡ ELECTRIC VIBE   │ 🪨 HIGH CONTRAST ANCHOR  │ 💊 TACTILE PILL SHAPES  │
│ Gradien Neon Lime │ Dark Slate pekat         │ Sudut kurva super bulat │
│ (#B5F942) dan     │ (#14161D) untuk hero     │ (r: 20-28px), badge tag │
│ Lavender pastel   │ card & floating navbar   │ kapsul (r: 999px), serta│
│ sebagai stimulan  │ menciptakan kontras      │ komponen modular yang   │
│ fokus & energi.   │ tajam, elegan & stabil.  │ kenyal dan interaktif.  │
└───────────────────┴──────────────────────────┴─────────────────────────┘
```

1. **Electric Vibe & Dopamine Triggers:** Palet warna utama *Electric Lime Green* dipadukan dengan aksen *Pastel Lilac/Lavender* dan *Sunset Orange* menghadirkan atmosfer ceria, segar, dan berenergi tinggi. Menghilangkan stigma bahwa aplikasi belajar teknologi harus kaku, monokromatik, atau membosankan.
2. **High-Contrast Dark Slate Anchors:** Elemen hitam pekat (*Charcoal/Dark Slate*) digunakan sebagai jangkar (*visual anchor*) pada banner hero utama, bilah navigasi melayang (*floating navbar*), dan tombol aksi kunci (*CTA*). Kontras tajam ini menjaga keterbacaan tingkat tinggi (WCAG AAA) sekaligus memberikan nuansa tech modern.
3. **Tactile Pill Geometry & Modular Cards:** Sudut komponen dirancang tumpul dan empuk (*large border-radius* 20–28px), elemen tombol dan status badge berbentuk kapsul penuh (*pill shape*, radius 999px), serta kartu asimetris yang menyerupai balok mainan modular fisik yang memuaskan saat disentuh (*tactile satisfaction*).

---

## 2. Color System & Design Tokens

Sistem warna diekstrak langsung dari referensi visual dan diselaraskan dengan kebutuhan PRD Progressio (gamifikasi XP, streak api, nyawa/hearts, dan verifikasi sertifikat blockchain).

```
       ELECTRIC LIME             PASTEL LAVENDER             DARK SLATE
     ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
     │  #B5F942 (Main) │       │  #DDD3FF (Soft) │       │  #14161D (Card) │
     │  #8DE319 (Deep) │       │  #7B4FE3 (Bold) │       │  #1A1C23 (Nav)  │
     └─────────────────┘       └─────────────────┘       └─────────────────┘
```

### 2.1 Core Palette Tokens

| Token Name | Hex Code | Deskripsi & Penggunaan UI |
|---|---|---|
| `limePrimary` | `#B5F942` | Warna brand utama, header gradient, active indicator, XP glow |
| `limeDeep` | `#8DE319` | Akhir gradien lime, border highlight, active tab badge |
| `limeLight` | `#E8FDC9` | Background kartu sub-fitur, surface aksen cerah |
| `darkSlate` | `#14161D` | Background kartu hero, teks headline utama, floating navbar |
| `darkCard` | `#1D2027` | Surface kartu dark mode / kartu hero sekunder |
| `lavenderBg` | `#EDE6FF` | Background kartu kategori sekunder, quiz choice box |
| `lavenderPrimary` | `#7B4FE3` | Badge "Hot", status pill aktif, ikon penanda materi |
| `coralOrange` | `#FF623E` | Streak fire 🔥, banner promo/challenge, alert timer |
| `sunYellow` | `#FDE93A` | Tag harga/poin, XP token, bintang reward ⭐ |
| `canvasBg` | `#F7FAF4` | Background halaman aplikasi (off-white gading segar) |
| `surfaceWhite` | `#FFFFFF` | Background kartu modul, list item, modal dialog |
| `textMain` | `#111317` | Teks judul utama, angka skor (Super High Contrast) |
| `textMuted` | `#727782` | Teks sekunder, deskripsi, placeholder input |
| `borderColor` | `#EAEFE3` | Outline kartu halus, pembatas list |

### 2.2 Gamification Semantic Tokens

| Token | Hex | Konteks Penggunaan |
|---|---|---|
| `heartRed` | `#FF4757` | Sisa nyawa (*Hearts*) & animasi jawaban salah |
| `streakFire` | `#FF623E` | Ikon api streak aktif & banner countdown tantangan harian |
| `xpGold` | `#FFC800` | XP counter, level progress bar, badge pencapaian |
| `successGreen` | `#22C55E` | Jawaban kuis benar, skill verified, status lulus |
| `lockedGray` | `#CBD5E1` | Node roadmap terkunci, tombol belum aktif |
| `blockchainCyan`| `#00D2D3` | Badge verifikasi sertifikat terdesentralisasi |

### 2.3 Dart Implementation (`lib/core/constants/app_colors.dart`)

```dart
import 'package:flutter/material.dart';

class AppColors {
  // Brand Lime Dopamine
  static const Color limePrimary = Color(0xFFB5F942);
  static const Color limeDeep = Color(0xFF8DE319);
  static const Color limeLight = Color(0xFFE8FDC9);

  // High Contrast Dark Anchors
  static const Color darkSlate = Color(0xFF14161D);
  static const Color darkCard = Color(0xFF1D2027);

  // Playful Dopamine Accents
  static const Color lavenderBg = Color(0xFFEDE6FF);
  static const Color lavenderPrimary = Color(0xFF7B4FE3);
  static const Color coralOrange = Color(0xFFFF623E);
  static const Color sunYellow = Color(0xFFFDE93A);

  // Background & Surfaces
  static const Color canvasBg = Color(0xFFF7FAF4);
  static const Color surfaceWhite = Color(0xFFFFFFFF);
  static const Color borderColor = Color(0xFFEAEFE3);

  // Typography
  static const Color textMain = Color(0xFF111317);
  static const Color textMuted = Color(0xFF727782);

  // Gamification Semantics
  static const Color heartRed = Color(0xFFFF4757);
  static const Color streakFire = Color(0xFFFF623E);
  static const Color xpGold = Color(0xFFFFC800);
  static const Color successGreen = Color(0xFF22C55E);
  static const Color lockedGray = Color(0xFFCBD5E1);
  static const Color blockchainCyan = Color(0xFF00D2D3);

  // Gradients
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
```

---

## 3. Typography & Text Hierarchy

Kombinasi 3 font family untuk fungsi spesifik:
* **Plus Jakarta Sans:** Font utama untuk headline, judul modul, tombol, dan badge status. Memiliki kurva ramah namun berkarakter tegas.
* **Inter:** Font keterbacaan tinggi untuk materi pelajaran panjang (*reading lessons*), penjelasan jawaban, dan instruksi.
* **JetBrains Mono:** Font monospace untuk baris kode, snippet interaktif, dan hash blockchain.

### 3.1 Type Scale Specification

| Token Level | Font Family | Size | Weight | Line Height | Case / Tracking | Contoh Penggunaan |
|---|---|---|---|---|---|---|
| `display1` | Plus Jakarta Sans | 32sp | 800 (ExtraBold) | 38sp | Regular / -0.5 | Angka skor level up, selamat! |
| `headline1` | Plus Jakarta Sans | 24sp | 700 (Bold) | 30sp | Regular / -0.3 | Judul Hero Banner, Judul Halaman |
| `headline2` | Plus Jakarta Sans | 20sp | 700 (Bold) | 26sp | Regular / 0.0 | Nama Skill di Learning Path, Modal Title |
| `subtitle1` | Plus Jakarta Sans | 16sp | 600 (SemiBold) | 22sp | Regular / 0.0 | Judul Card Modul, Nama Track |
| `subtitle2` | Plus Jakarta Sans | 14sp | 600 (SemiBold) | 18sp | Regular / 0.0 | Label Kategori, Chip Filter Tab |
| `body1` | Inter | 15sp | 400 (Regular) | 22sp | Regular / 0.1 | Materi Pembelajaran (Reading Lesson) |
| `body2` | Inter | 13sp | 500 (Medium) | 18sp | Regular / 0.1 | Subteks statistik, deskripsi kartu |
| `captionTag` | Plus Jakarta Sans | 11sp | 800 (ExtraBold) | 14sp | Uppercase / 0.5 | Badge "HOT", "9折", Tag XP "+15 XP" |
| `codeBlock` | JetBrains Mono | 13sp | 500 (Medium) | 20sp | Monospace / 0.0 | Code snippet, fill-in-blank exercise |

---

## 4. Spacing, Geometry, & Elevation

### 4.1 Spacing Scale

```dart
class AppSpacing {
  static const double xs = 4.0;    // Icon padding, tag spacing
  static const double sm = 8.0;    // Internal chip padding, compact row gap
  static const double md = 12.0;   // Inner card padding, list gap
  static const double lg = 16.0;   // Screen horizontal padding, section gap
  static const double xl = 24.0;   // Major card gap, hero spacing
  static const double xxl = 32.0;  // Large section separation
}
```

### 4.2 Border Radius Constants

* **Pill / Capsule (Buttons, Badges, Search Bar):** `BorderRadius.circular(999.0)`
* **Floating Bottom Nav Bar:** `BorderRadius.circular(36.0)`
* **Hero Banner Card:** `BorderRadius.circular(26.0)`
* **Modular Cards (Grid & List):** `BorderRadius.circular(24.0)`
* **Input Fields & Code Boxes:** `BorderRadius.circular(16.0)`

### 4.3 Depth & Elevation (Soft Dopamine Shadows)

Hindari shadow pekat hitam kotor. Gunakan shadow halus dengan sebaran luas atau colored glow:

```dart
class AppShadows {
  static List<BoxShadow> softCardShadow = [
    BoxShadow(
      color: const Color(0xFF14161D).withOpacity(0.04),
      blurRadius: 16,
      offset: const Offset(0, 8),
    ),
  ];

  static List<BoxShadow> floatingNavShadow = [
    BoxShadow(
      color: const Color(0xFF14161D).withOpacity(0.35),
      blurRadius: 24,
      offset: const Offset(0, 10),
    ),
  ];

  static List<BoxShadow> limeGlow = [
    BoxShadow(
      color: const Color(0xFFB5F942).withOpacity(0.45),
      blurRadius: 18,
      offset: const Offset(0, 6),
    ),
  ];
}
```

---

## 5. Master Component Library

### 5.1 Floating Pill Bottom Navigation Bar
Mengadopsi bilah navigasi mengambang warna *Dark Slate* kapsul dari referensi visual.

```
┌─────────────────────────────────────────────────────────────┐
│    ╭───────────────────────────────────────────────────╮    │
│    │   ( 🏠 )      [ 📚 ]      [ ⚔️ ]      [ 🏆 ]    [ 👤 ] │    │
│    │   Beranda    Belajar    Tantangan   Sertifikat   Profil│   │
│    ╰───────────────────────────────────────────────────╯    │
└─────────────────────────────────────────────────────────────┘
```

* **Spesifikasi Posisi:** Floating di atas konten, `margin: EdgeInsets.fromLTRB(16, 0, 16, 18)`.
* **Dimensi:** Height 68dp, background `AppColors.darkSlate`, border radius 36dp.
* **Active Indicator:** Kapsul neon lime (`#B5F942`) dengan teks label tebal hitam dan ikon hitam solid.
* **Inactive State:** Ikon putih transparan (`white60`), tanpa label teks saat tidak aktif agar bilah navigasi tetap lega dan ringkas.

### 5.2 Header Gradien & Stat Capsules
* **Header Curved Gradient:** Background atas menggunakan `AppColors.limeHeaderGradient` yang melengkung lembut ke bawah.
* **Stat Capsules:** Tiga kapsul berderet di samping avatar:
  * **Streak:** Kapsul oranye lembut dengan ikon api `🔥` dan angka streak.
  * **Hearts:** Kapsul merah muda lembut dengan ikon hati `❤️` dan sisa nyawa (misal `5/5`).
  * **XP:** Kapsul kuning lembut dengan ikon petir `⚡` dan jumlah poin.
* **Search Pill:** Kolom pencarian putih bersih melengkung penuh (`radius: 999`), placeholder abu-abu netral *"Ketik materi atau bahasa..."* dengan ikon kaca pembesar di sisi kiri.

### 5.3 Asymmetric Modular Cards (Grid 2x2)
* **Kartu A (Lime Tint):**
  * Latar belakang: `AppColors.limeLight` (`#E8FDC9`).
  * Ikon: Kotak tumpul warna oranye tebal berikon putih (misal ikon `Headphones` atau `Code`).
  * Label Tag: Kapsul hijau daun bertuliskan *"Populer"*.
  * Footnote: Tag kuning bertuliskan poin reward `+20 XP`.
* **Kartu B (Lavender Tint):**
  * Latar belakang: `AppColors.lavenderBg` (`#EDE6FF`).
  * Label Tag: Kapsul ungu pekat bertuliskan *"HOT"* dengan font tebal.
  * Tag reward poin kapsul kuning di sisi bawah.

### 5.4 Hero Dark Card Banner
* **Background:** `AppColors.darkSlate` dengan dekorasi tipis watermark kode di background.
* **Konten Kiri:** Tag pill ungu bertuliskan *"TRACK UTAMA"*, judul tebal putih *"Flutter Mobile Dev"*, progress bar lime neon, dan tombol pill *"Lanjut Belajar"*.
* **Konten Kanan (3D Element Overlap):** Maskot buku coding atau kubus neon 3D yang posisinya sedikit keluar dari batas kartu atas (*overlapping margin*), dilengkapi stiker diskon/bonus kuning bergigi (badge bintang diskon 9折 ala referensi).

### 5.5 Duolingo-style Skill Path Node (Learning Path)
* **Bentuk Node:** Lingkaran diameter 78dp dengan efek bantalan 3D 4dp pada dasar node.
* **Connecting Line:** Garis lengkung tebal (stroke 6dp) dengan warna abu-abu kehijauan lembut.
* **Variasi State:**
  * **Terkunci (Locked):** Warna abu-abu (`#CBD5E1`) dengan ikon gembok perak.
  * **Tersedia (Available):** Warna putih dengan border tebal `limeDeep`, ikon play hitam, siap dipelajari.
  * **Sedang Berjalan (In Progress):** Lingkaran progress ring melingkari node + denyut animasi (*pulse glow*).
  * **Tuntas (Mastered):** Warna penuh `limePrimary` dengan ikon mahkota atau bintang emas.
  * **Checkpoint / Boss Node:** Node berbentuk perisai heksagonal besar pada akhir setiap kompetensi untuk assessment sertifikasi.

### 5.6 Interactive Checkpoint & Feedback Bottom Sheet
* **Choice Card Pill:** Pilihan jawaban multiple-choice berbentuk kartu kapsul tinggi 56dp. Saat dipilih, outline berubah menjadi `lavenderPrimary` dengan background `lavenderBg`.
* **Code Blank Box:** Potongan kode dengan slot kosong berlatar belakang gelap, user menekan tombol pill kata dari *word bank* di bawah untuk mengisi kekosongan.
* **Feedback Sheet Sukses:**
  * Background: `AppColors.limeLight` (`#E8FDC9`).
  * Ikon: Centang hijau ceria dalam lingkaran putih.
  * Pesan: *"Hebat! Solusimu Tepat!"* + floating tag `+10 XP`.
  * Tombol CTA: Kapsul hitam pekat bertuliskan *"Lanjutkan"*.
* **Feedback Sheet Gagal:**
  * Background: `#FFEAEA`.
  * Ikon: Hati bergetar `-1 ❤️`.
  * Penjelasan: Jawaban benar beserta ulasan sintaks.
  * Tombol CTA: Kapsul merah muda bertuliskan *"Mengerti"*.

---

## 6. Spesifikasi Visual Layar Utama (Screen Specs)

### 6.1 Splash Screen & Onboarding
* **Splash Screen:** Background `darkSlate`, logo Progressio bersinar dalam gradien lime, tagline *"Turning Progress Into Proof"* muncul dengan animasi fade-in lembut.
* **Onboarding (3 Slides):** Latar belakang canvas off-white gading `#F7FAF4`. Setiap slide memiliki ilustrasi 3D dopamine penuh warna di bagian atas (60% layar), judul tebal Plus Jakarta Sans 24sp, dot indicator berbentuk kapsul memanjang, dan tombol pill utama di bawah.

### 6.2 Interest Selector (`interest_selector/`)
* **Header:** Teks tebal *"Apa yang ingin kamu kuasai?"* dengan subteks abu-abu netral.
* **Grid Topik:** Kartu chip tinggi 64dp berbentuk rounded 20dp:
  * State unselected: Surface putih, outline tipis `borderColor`, teks hitam.
  * State selected: Background `limeLight`, outline tebal 2dp `limeDeep`, ikon centang hijau neon.

### 6.3 Home Dashboard (`home/`)

```
┌─────────────────────────────────────────────────────────────┐
│  [Avatar]  🔥 12   ❤️ 5   ⚡ 1,420                      🔔 │  <- Header Lime
│  ╭───────────────────────────────────────────────────────╮  │
│  │ 🔍 Cari materi pemrograman, skill, atau track...      │  │
│  ╰───────────────────────────────────────────────────────╯  │
├─────────────────────────────────────────────────────────────┤
│  ╭─────────────────────────────────────────────────────╮    │
│  │ 🚀 LANJUTKAN TRACK                   [⭐ BONUS XP]  │    │  <- Dark Slate
│  │ Mobile Engineer with Flutter                        │    │     Hero Card
│  │ [██████████████░░░░░] 68%          ( Belajar > )    │    │
│  ╰─────────────────────────────────────────────────────╯    │
│                                                             │
│  [Semua]  [Frontend]  [Backend]  [Mobile]  [Cloud]          │  <- Filter Pills
│                                                             │
│  ╭────────────────────────╮  ╭──────────────────────────╮   │
│  │ 🟢 Dart OOP & Async    │  │ 🟣 Flutter State BLoC    │   │  <- Asymmetric
│  │ 240 Siswa Terdaftar    │  │ HOT 🔥                   │   │     Dopamine
│  │ [ +50 XP ]             │  │ [ +80 XP ]               │   │     Cards
│  ╰────────────────────────╯  ╰──────────────────────────╯   │
│                                                             │
│  ╭─────────────────────────────────────────────────────╮    │
│  │ ⚔️ Tantangan Harian: Algoritma Rekursi     04:12:10 │    │  <- Challenge
│  ╰─────────────────────────────────────────────────────╯    │
│                                                             │
│       ╭───────────────────────────────────────────╮         │
│       │   🏠       📚       ⚔️       🏆       👤   │         │  <- Floating Nav
│       ╰───────────────────────────────────────────╯         │
└─────────────────────────────────────────────────────────────┘
```

### 6.4 Learning Path (`learning_path/`)
* **Peta Belajar Vertikal:** Garis jalur meliuk di tengah dengan node skill yang tersusun zig-zag.
* **Indikator Posisi Saat Ini:** Balon avatar bergerak (*bouncing pin*) tepat di atas skill aktif.
* **Stat Bar Mengambang di Atas:** Bilah mini putih di bawah app bar yang menampilkan sisa nyawa dan streak tanpa menghalangi peta.

### 6.5 Credential & Blockchain Detail (`credential_detail/`)
* **Sertifikat Preview Card:** Kartu elegan bernuansa hitam obsidian (`#111317`) dengan rasio 4:3, border gradien emas-lime, logo Progressio, dan stempel digital *Verified*.
* **Status Verifikasi Blockchain:**
  * Box status berlatar belakang `lavenderBg` dengan teks hash transaksi (truncated) dan status *"Verified on Polygon POS"*.
  * QR Code scannable berukuran besar di bagian tengah untuk pembuktian publik langsung.
  * Dua tombol pill aksi di bawah: *"Bagikan ke LinkedIn / Medsos"* (Dark Slate) dan *"Unduh PDF"* (Outline).

---

## 7. Komponen Kode Flutter Siap Pakai

Implementasi widget inti berada di direktori `lib/presentation/widgets/`.

### 7.1 Reusable Dopamine Pill Button (`dopamine_button.dart`)
* Implementasi tombol berbentuk pill kapsul dengan 3 varian: `primaryLime`, `darkSlate`, dan `secondaryLavender`.

### 7.2 Floating Pill Bottom Navigation Bar (`floating_nav_bar.dart`)
* Implementasi navbar kapsul mengambang (floating) dengan active pill neon lime dan background dark slate.

### 7.3 Asymmetric Modular Card Widget (`modular_feature_card.dart`)
* Implementasi kartu asimetris modular untuk home dashboard (varian tone `lime` dan `lavender`).

---

## 8. Panduan Animasi & Haptik

Untuk menghasilkan *tactile dopamine satisfaction*:

1. **Micro-tap Haptic:** Panggil `HapticFeedback.lightImpact()` pada setiap kali menekan pilihan kuis, opsi tab navigasi, dan filter chip.
2. **Success Burst (Jawaban Benar):** Panggil `HapticFeedback.mediumImpact()` disertai animasi scale bounce kartu `0.95 -> 1.05 -> 1.0` (durasi 250ms) dan ledakan konfeti mini.
3. **XP Float Animation:** Partikel teks emas `+15 XP` melayang ke atas (*float up*) sejauh 40dp sambil memudar (*fade out*) selama 800ms menggunakan `AnimatedOpacity` dan `SlideTransition`.
4. **Streak Flame Flicker:** Integrasi animasi Rive/Lottie pada ikon api di header agar bergetar lembut secara berkala, memberi kesan streak user tetap berkobar.

---

## 9. Penyesuaian Theme Data Flutter (`app_theme.dart`)

Theme global aplikasi telah diatur pada `lib/core/theme/app_theme.dart` menggunakan method `AppTheme.dopamineTheme`.

---
*Dokumen ini merupakan standar resmi acuan implementasi UI/UX Mobile Progressio.*
