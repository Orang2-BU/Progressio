# ⚙️ WORKFLOW — Aturan Main untuk AI

> File ini mengatur kapan AI boleh jalan sendiri, kapan harus minta izin, dan kapan fitur dianggap selesai.

---

## Scope: Khusus Mobile

**Semua file di `Mobile/docs/` HANYA berlaku saat mengerjakan folder `Mobile/`.**

Jika sedang kerja di `back-end/`, `front-end/`, atau `curriculum/` → **ABAIKAN** seluruh isi folder `Mobile/docs/`. Dokumen-dokumen ini tidak relevan untuk bagian lain dari project.

---

## Sebelum Mulai Kerja

**WAJIB baca urut:**

1. **`docs/TODO.md`** — Lihat status terkini, apa yang sudah selesai, apa yang sedang dikerjakan
2. **`docs/ARCHITECTURE.md`** — Pahami struktur folder dan aturan layer
3. **`docs/AGENTS.md`** — Pahami coding style dan konvensi

Baca **`docs/design/DESIGN.md`** DAN cek folder **`docs/design/figma_screens/`** ketika mengerjakan UI/widget/halaman agar tampilan sesuai acuan visual Figma.
Baca `docs/PRD_MOBILE.md` **hanya jika** butuh detail spesifikasi fitur, flow bisnis, atau gamifikasi.
Baca `docs/SKILL.md` **hanya jika** perlu template prompt.

---

## Boleh Jalan Sendiri (Tanpa Izin)

AI **BOLEH langsung kerjakan** tanpa minta konfirmasi jika:

- Membuat file baru yang sudah ada di ARCHITECTURE.md (entity, model, repo, usecase, BLoC, page)
- Menambah konstanta baru di `app_colors.dart`, `app_strings.dart`, `app_spacing.dart`, `api_constants.dart`
- Membuat widget di folder yang benar (`widgets/` atau `pages/<nama>/widgets/`)
- Fix bug kecil (typo, import salah, null check, format)
- Menambah route di `app_router.dart`
- Update `TODO.md` (ubah status task)
- Menjalankan `flutter analyze` atau `flutter test`

---

## Harus Minta Izin Dulu

AI **WAJIB tanya user** sebelum:

- Mengubah arsitektur (pindah layer, ubah folder structure)
- Mengganti library/package (misal ganti BLoC ke Riverpod)
- Menghapus file yang sudah ada
- Mengubah design system (warna, font, spacing yang sudah ditetapkan)
- Menambah dependency baru di `pubspec.yaml`
- Mengubah `main.dart` atau `app.dart` secara signifikan
- Menyentuh folder `android/` atau `ios/`
- Mengerjakan task yang **belum ada** di TODO.md (fitur di luar PRD)
- Mengubah isi file docs (PRD, ARCHITECTURE, AGENTS, WORKFLOW)

---

## Saat Ganti Section / Fitur

Ketika pindah mengerjakan task atau section yang berbeda:

1. **Baca `TODO.md`** — cek status terkini
2. **Update task sebelumnya** — tandai `✅` jika selesai, `🔄` jika setengah jalan
3. **Tandai task baru** — ubah status ke `🔄`
4. **Lanjut kerja**

Jangan lompat ke task baru tanpa update status task lama.

---

## Definisi "Selesai"

Sebuah fitur/halaman dianggap **✅ Selesai** jika:

- [ ] Semua file terbuat di folder yang benar (sesuai ARCHITECTURE.md)
- [ ] Tidak ada hardcode warna/font/spacing/string — semua dari constants
- [ ] Handle 4 state UI: loading (shimmer), loaded, empty, error
- [ ] Route terdaftar di `app_router.dart`
- [ ] Endpoint terdaftar di `api_constants.dart`
- [ ] `AppStrings` diupdate untuk teks UI baru
- [ ] Kode lolos `flutter analyze` tanpa warning
- [ ] `TODO.md` diupdate (status → `✅`, log perubahan diisi)

Jika salah satu belum terpenuhi → status tetap `🔄`, bukan `✅`.

---

## Urutan Kerja per Task

```
1. Baca TODO.md           → cek task mana yang dikerjakan
2. Baca PRD (jika perlu)  → pahami spesifikasi fitur
3. Kerjakan domain/       → entity + repository interface + usecase
4. Kerjakan data/         → model + repository impl + datasource
5. Kerjakan presentation/ → Cek mockup di docs/design/figma_screens/ + implementasi BLoC/Cubit + page + widgets
6. Update constants       → strings, colors, api endpoints (jika ada yang baru)
7. Update router          → tambah route di app_router.dart
8. Cek kualitas           → flutter analyze, tidak ada hardcode, cocokkan dengan mockup
9. Update TODO.md         → status ✅ + log perubahan
```

---

## Ringkasan Peta Dokumen

```
Mobile/
└── docs/
    ├── TODO.md            ← ⭐ BACA PERTAMA — status & memori project
    ├── ARCHITECTURE.md    ← Struktur folder, layer, design system quick ref
    ├── AGENTS.md          ← Coding style, konvensi, anti-pattern
    ├── PRD_MOBILE.md      ← Spesifikasi fitur, halaman, gamifikasi
    ├── NATIVE_PLATFORMS.md ← Kapan sentuh android/ dan ios/
    ├── SKILL.md           ← Template prompt reusable
    ├── WORKFLOW.md        ← (file ini) Aturan main
    │
    └── design/            ← 🎨 SPESIFIKASI DESAIN & MOCKUP FIGMA
        ├── DESIGN.md      ← Token warna, tipografi, radius, dan panduan UI
        ├── figma_screens/ ← Screenshot halaman Figma untuk acuan visual AI
        └── components/    ← Screenshot potongan komponen modular
```
