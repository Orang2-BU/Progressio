# 🛠️ SKILL — Pola Prompt Reusable

> File ini berisi template prompt yang bisa dipakai berulang.
> Copy-paste ke chat AI, ganti placeholder `{...}`, jalankan.

---

## Skill 1: Buat Halaman Baru (End-to-End)

**Kapan dipakai:** Setiap kali butuh halaman baru lengkap dari domain sampai UI.

```
Buatkan halaman {NAMA_HALAMAN} untuk Progressio Mobile.

Konteks:
- Halaman ini berfungsi untuk {DESKRIPSI_FUNGSI}.
- Data diambil dari endpoint: {METHOD} {ENDPOINT}
- Response JSON contoh:
{CONTOH_JSON}

Buatkan lengkap end-to-end sesuai ARCHITECTURE.md dan AGENTS.md:

1. domain/entities/{nama}.dart
2. data/models/{nama}_model.dart — fromJson/toJson, extends entity
3. domain/repositories/{nama}_repository.dart — Interface abstract
4. data/repositories/{nama}_repository_impl.dart
5. data/datasources/remote/{nama}_remote_datasource.dart
6. domain/usecases/{nama}_usecase.dart
7. presentation/pages/{nama}/bloc/{nama}_cubit.dart + state
8. presentation/pages/{nama}/{nama}_page.dart
9. presentation/pages/{nama}/widgets/ — Widget khusus (jika perlu)

Aturan:
- Periksa gambar mockup di docs/design/figma_screens/ jika ada, jadikan acuan layout 1:1
- Warna dari AppColors, spacing dari AppSpacing, string dari AppStrings
- Loading pakai skeleton shimmer, bukan spinner
- Handle 4 state: loading, loaded, empty, error
- Navigasi pakai GoRouter
- Tambahkan route di app_router.dart
- Tambahkan endpoint di api_constants.dart jika belum ada
- Update TODO.md setelah selesai
```

---

## Skill 2: Buat Widget Reusable

**Kapan dipakai:** Butuh widget baru yang dipakai di ≥2 halaman.

```
Buatkan widget reusable {NAMA_WIDGET} untuk Progressio Mobile.

Konteks:
- Widget ini berfungsi untuk {DESKRIPSI_FUNGSI}.
- Dipakai di halaman: {DAFTAR_HALAMAN}.
- Kategori widget: {common/buttons/cards/inputs/dialogs/indicators/gamification}

Taruh di: presentation/widgets/{kategori}/{nama_widget}.dart

Aturan:
- Periksa gambar contoh di docs/design/components/ jika ada
- Pakai const constructor
- Warna/spacing/radius dari constants, JANGAN hardcode
- Parameternya lengkap (required + optional yang masuk akal)
- Responsive: jangan hardcode width/height
- Tambahkan doc comment /// di atas class
- Contoh penggunaan di doc comment
```

---

## Skill 3: Integrasi API Endpoint Baru

**Kapan dipakai:** Backend menambah endpoint baru yang perlu diintegrasikan ke mobile.

```
Integrasikan endpoint baru ke Progressio Mobile.

Endpoint:
- Method: {GET/POST/PUT/DELETE}
- URL: {FULL_ENDPOINT}
- Auth: {Bearer JWT / Public}
- Request body: {JSON_BODY atau "tidak ada"}
- Response JSON contoh:
{CONTOH_RESPONSE}

Buatkan/update file berikut:
1. Tambah constant di api_constants.dart
2. data/models/{nama}_model.dart — fromJson/toJson
3. data/datasources/remote/{nama}_remote_datasource.dart — method baru
4. domain/repositories/{nama}_repository.dart — tambah method interface
5. data/repositories/{nama}_repository_impl.dart — implementasi
6. domain/usecases/{nama}_usecase.dart — jika aksi baru

Jangan buat halaman — hanya data layer dan domain layer saja.
Update TODO.md setelah selesai.
```

---

## Skill 4: Testing

**Kapan dipakai:** Perlu buat unit test atau widget test.

### 4a. Unit Test (UseCase / Model)

```
Buatkan unit test untuk {NAMA_CLASS} di Progressio Mobile.

File yang ditest: {PATH_FILE}

Buatkan di: test/{mirror_path}_test.dart

Aturan:
- Nama test: 'should {expected} when {condition}'
- Pakai pattern arrange → act → assert
- Mock dependency pakai mockito atau manual mock
- Cover: happy path, error case, edge case
- Group berdasarkan method/function
```

### 4b. Widget Test

```
Buatkan widget test untuk halaman {NAMA_PAGE} di Progressio Mobile.

File yang ditest: {PATH_FILE}

Test yang dibutuhkan:
- Render loading state (shimmer muncul)
- Render loaded state (data tampil benar)
- Render empty state (pesan empty muncul)
- Render error state (pesan error + tombol retry muncul)
- Interaksi: tap {ELEMEN} → {EXPECTED_BEHAVIOR}

Mock semua dependency (BLoC/Cubit, repository).
```

---

## Skill 5: Bug Fix / Debugging

**Kapan dipakai:** Ada bug yang perlu didiagnosa dan diperbaiki.

```
Fix bug di Progressio Mobile.

Masalah:
- Halaman/widget: {NAMA_HALAMAN_ATAU_WIDGET}
- Gejala: {DESKRIPSI_BUG}
- Langkah reproduksi: {LANGKAH_1, LANGKAH_2, ...}
- Expected: {YANG_SEHARUSNYA_TERJADI}
- Actual: {YANG_TERJADI}
- Error message (jika ada): {ERROR_LOG}

Tolong:
1. Diagnosa root cause
2. Jelaskan kenapa bug terjadi
3. Fix bug-nya
4. Pastikan fix tidak merusak bagian lain
5. Update TODO.md jika relevan
```

---

## Skill 6: Refactoring / Code Cleanup

**Kapan dipakai:** Kode sudah jalan tapi perlu dibersihkan.

```
Refactor {NAMA_FILE_ATAU_FOLDER} di Progressio Mobile.

Yang perlu diperbaiki:
- {MASALAH_1: misal "ada hardcode warna di widget"}
- {MASALAH_2: misal "function terlalu panjang, pecah jadi method kecil"}
- {MASALAH_3: misal "widget ini harusnya reusable, pindah ke widgets/"}

Aturan refactor:
- Jangan ubah behavior/logic — hanya struktur dan kebersihan
- Pastikan masih compile dan jalan setelah refactor
- Pindahkan hardcode ke constants jika ditemukan
- Pecah widget besar (>100 baris build method) jadi sub-widget
- Pastikan naming convention sesuai AGENTS.md
- Jangan hapus komentar/docstring yang sudah ada
```

---

## Skill 7: Security Review

**Kapan dipakai:** Review keamanan sebelum rilis atau setelah fitur auth/credential.

```
Lakukan security review pada {SCOPE} di Progressio Mobile.

Scope: {file/folder/fitur yang direview}

Checklist review:
1. JWT token disimpan di flutter_secure_storage, BUKAN SharedPreferences
2. Token tidak di-log atau di-print ke console
3. Tidak ada hardcode API key, secret, atau credential
4. Password field pakai obscureText: true
5. Input user di-sanitasi sebelum dikirim ke API
6. Tidak ada data sensitif di-cache tanpa enkripsi
7. Certificate pinning dipertimbangkan untuk production
8. Deep link tidak mengekspos route sensitif tanpa auth guard
9. Error message tidak mengekspos detail internal (stack trace, SQL, dll)

Laporkan:
- ✅ Aman
- ⚠️ Perlu perbaikan (jelaskan + fix)
- ❌ Vulnerability (jelaskan + fix segera)
```

---

## Skill 8: Code Review / Quality Check

**Kapan dipakai:** Setelah selesai buat fitur, review kualitas sebelum lanjut.

```
Review kualitas kode di {SCOPE} Progressio Mobile.

Scope: {file/folder yang direview}

Checklist:
1. ARSITEKTUR — File di layer dan folder yang benar?
2. CONSTANTS — Tidak ada hardcode warna/font/spacing/string/endpoint?
3. NAMING — File snake_case, class PascalCase, suffix sesuai (Page/Model/Cubit/dll)?
4. STATE — Pakai BLoC/Cubit, bukan setState untuk state kompleks?
5. ERROR — Handle loading, empty, error, offline?
6. IMPORT — Urutan benar (dart → flutter → 3rd party → project)?
7. WIDGET — Const constructor? Reusable di tempat yang benar?
8. NAVIGASI — Pakai GoRouter, bukan Navigator.push?
9. DOC — Ada docstring pada class dan method publik?
10. ANTI-PATTERN — Tidak ada item dari daftar "Yang Dilarang" di AGENTS.md?

Laporkan per file:
- ✅ OK
- ⚠️ Minor (perbaiki)
- ❌ Harus diperbaiki (jelaskan)
```

---

## Skill 9: Performance Audit

**Kapan dipakai:** App terasa lambat, atau sebelum rilis production.

```
Audit performa {SCOPE} di Progressio Mobile.

Scope: {file/folder/seluruh app}

Checklist:
1. Tidak ada rebuild widget yang tidak perlu (pakai const, BlocSelector, BlocBuilder targeted)
2. ListView/GridView pakai .builder (lazy loading), bukan children langsung
3. Image pakai CachedNetworkImage, bukan Image.network
4. Tidak ada async call di build method
5. Heavy computation tidak di main isolate
6. Animasi pakai AnimatedBuilder/TweenAnimationBuilder, bukan setState
7. MediaQuery pakai .sizeOf(context) bukan .of(context).size
8. Tidak ada unnecessary re-render karena BLoC state selalu emit object baru
9. Offline cache TTL sesuai (lihat PRD section 13)

Laporkan:
- ✅ Optimal
- ⚠️ Bisa dioptimalkan (jelaskan caranya)
- ❌ Performance issue (jelaskan + fix)
```
