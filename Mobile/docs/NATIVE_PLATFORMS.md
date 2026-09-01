# 📱 Panduan Platform Native (Folder `android/` dan `ios/`)

Dokumen ini menjelaskan fungsi, struktur, dan kapan kamu perlu menyentuh folder `android/` dan `ios/` di dalam project Flutter **Progressio Mobile**.

---

## 🎯 Mengapa Ada Folder `android/` dan `ios/`?

Flutter adalah framework **cross-platform**. Kamu menulis logika aplikasi dan antarmuka (UI) sekali saja menggunakan bahasa **Dart** di dalam folder `lib/`.

Namun, sistem operasi Android dan iOS memiliki arsitektur, format packaging, dan sistem perizinan yang sangat berbeda:
- Android membutuhkan project berbasis **Gradle & Kotlin** untuk menghasilkan file `.apk` atau `.aab` (Google Play Store).
- iOS membutuhkan project berbasis **Xcode & Swift** untuk menghasilkan file `.ipa` (Apple App Store).

Folder `android/` dan `ios/` adalah **jembatan dan wadah *native runner*** yang membungkus kode Flutter kamu agar bisa dijalankan di kedua platform tersebut.

```text
                               ┌──▶ [android/] ──▶ Compile ke .apk / .aab (Play Store)
[lib/ (Dart UI & Logic)] ──────┤
                               └──▶ [ios/]     ──▶ Compile ke .ipa (App Store)
```

---

## 🤖 1. Bedah Folder `android/`

Folder ini adalah struktur project standar Android native.

### File-file Penting yang Sering Digunakan:

| Path File | Fungsi Utama |
|---|---|
| `app/src/main/AndroidManifest.xml` | **Izin Aplikasi & Konfigurasi Inti:** Menambahkan permission (Internet, Kamera, Penyimpanan, Lokasi, Bluetooth), nama aplikasi di HP, dan orientasi layar. |
| `app/build.gradle.kts` | **Pengaturan Build Level Aplikasi:** Mengatur `applicationId`, `minSdk` (versi Android terendah), `targetSdk`, `versionCode`, dan `versionName`. |
| `build.gradle.kts` | **Pengaturan Build Level Project:** Repository Gradle dan plugin level atas. |
| `app/src/main/res/` | **Aset Resource Native:** Menyimpan icon launcher (`mipmap/`), warna splash screen native, dan layout awal saat app dibuka (*cold start*). |
| `app/src/main/kotlin/.../MainActivity.kt` | **Activity Utama:** Entry point native Android. Digunakan jika perlu membuat *MethodChannel* (komunikasi native kustom). |

### Contoh Kapan Harus Mengedit `android/`:
1. **Menambahkan Izin Internet:**
   ```xml
   <!-- Di AndroidManifest.xml -->
   <uses-permission android:name="android.permission.INTERNET"/>
   ```
2. **Mengganti Nama Aplikasi di Home Screen:**
   ```xml
   <!-- Di AndroidManifest.xml -->
   <application android:label="Progressio" ...>
   ```

---

## 🍎 2. Bedah Folder `ios/`

Folder ini adalah struktur project standar iOS/macOS berbasis Xcode.

### File-file Penting yang Sering Digunakan:

| Path File | Fungsi Utama |
|---|---|
| `Runner/Info.plist` | **Daftar Konfigurasi & Privasi Apple:** Menjelaskan izin akses privasi (Permission string, misal alasan akses kamera/galeri), bundle name, orientasi layar, URL scheme (Deep Link). |
| `Runner.xcodeproj/` | **Project File Xcode:** Konfigurasi build setting Xcode, target device, signing & certificate. |
| `Runner/Assets.xcassets/` | **Aset Native iOS:** Icon aplikasi untuk berbagai ukuran layar iPhone/iPad (`AppIcon.appiconset`) dan launch image. |
| `Runner/AppDelegate.swift` | **Entry Point iOS:** Inisialisasi service native iOS, push notification, atau *MethodChannel*. |
| `Podfile` | **Dependency Manager (CocoaPods):** Mengelola library native iOS yang dibutuhkan oleh package Flutter. |

### Contoh Kapan Harus Mengedit `ios/`:
1. **Menambahkan Deskripsi Privasi Kamera (Wajib di iOS):**
   ```xml
   <!-- Di Info.plist -->
   <key>NSCameraUsageDescription</key>
   <string>Progressio memerlukan akses kamera untuk verifikasi kartu identitas/asesmen.</string>
   ```
2. **Mengatur Target Versi iOS Minimal:**
   Dikonfigurasi di file `Podfile` (misalnya `platform :ios, '14.0'`).

---

## ⚖️ Kapan Harus Menyentuh vs Mengabaikan?

### ❌ JANGAN Sentuh (95% Waktu Ngoding):
- Menambah halaman baru (*UI screens*).
- Menambah state management, navigasi, atau business logic.
- Mengatur tema warna, font, dan animasi.
- Integrasi REST API dan pemrosesan data JSON.
👉 **Semuanya dilakukan di folder `lib/`.**

### ✅ PERLU Disentuh (5% Waktu Tertentu):
1. **Ganti Logo / App Icon:** Mengubah icon aplikasi di home screen HP.
2. **Tambah Hardware Permission:** Kamera, galeri, push notification, lokasi, Bluetooth.
3. **Konfigurasi Rilis (Production Build):** Keystore signing Android, provisioning profile iOS, dan version numbering sebelum upload ke Play Store / App Store.
4. **Deep Linking / OAuth Redirection:** Integrasi Google Sign-In atau pembayaran pihak ketiga.
