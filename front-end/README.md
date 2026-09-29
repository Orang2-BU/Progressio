# Progressio frontend

Frontend web Next.js App Router + React. Aplikasi Flutter tetap berada di `../Mobile/`.

## Status fase 1

Fondasi web tersedia: halaman daftar/masuk, ringkasan workspace, profil baca saja,
logout, proteksi halaman, validasi form, loading/error, dan layout responsif.
Registrasi dan profil menggunakan API Django, bukan data dummy. Role student dan
recruiter mengikuti backend; menu belajar/assessment belum diimplementasikan.
Warna mengikuti identitas aplikasi Mobile; form memakai label, fokus keyboard,
ringkasan error dan pesan status yang dapat diakses.

## Status fase 2 — katalog dan target

`/catalog` memakai API Django untuk memilih career track -> competency -> skill.
Semua halaman pagination dimuat untuk masing-masing cabang. Perubahan parent
mereset child; request lama dibatalkan agar respons terlambat tidak mengganti
pilihan baru. Loading, data kosong, error/retry, dan URL invalid dibedakan.

Cakupan target dapat career track, competency, atau skill. Ringkasan memakai ID,
slug dan hubungan parent yang dikembalikan server, bukan ID seed/hardcode.
Detail skill menampilkan prasyarat dan estimasi belajar. Memilih target tidak
mengubah mastery, XP, atau menerbitkan credential; jumlah materi bukan kriteria
credential. Kriteria lengkap/versi standar masih memerlukan backlog G8.

Pilihan tersimpan **hanya di URL**, contoh bentuk `/catalog?track={id}&competency={id}&skill={id}&target=skill`.
Tombol salin tautan memakai clipboard; jika izin ditolak, salin bilah alamat.
Reload meminta login ulang tetapi URL target dipulihkan melalui parameter `next`
yang dibatasi ke route internal. Back/Forward memulihkan pilihan. Ini bukan
preferensi akun lintas perangkat di backend. Navigasi ke `/catalog` tanpa query
memulai pilihan baru; gunakan URL target atau Back untuk membuka pilihan lama.

Scope fase 2 ini adalah katalog/pemilihan target. Diagnostic, roadmap, materi,
assessment dan credential belum menjadi fitur web yang selesai pada fase 2.

## Status fase 3 — diagnostic dan hasil

Target katalog diteruskan ke `/diagnostic`; soal diambil dari Django tanpa kunci
jawaban. Diagnostic tetap mencakup seluruh career track meskipun target competency
atau skill. Semua soal wajib dijawab, termasuk pilihan eksplisit “Belum tahu”
yang dinilai salah. Form memakai radio native, inline error, ringkasan error
berfokus, dan pengunci submit. Tidak ada skor yang dihitung/dikirim client.

`/diagnostic/result` menampilkan attempt terbaru dari server: skor keseluruhan,
skor/jumlah benar per skill, rekomendasi skill dan waktu selesai. URL menyimpan
target, bukan ID hasil tertentu. Reload meminta login ulang dan memuat hasil
terbaru; belum ada riwayat/detail attempt. Diagnostic tidak memberikan XP atau
credential. Mastery backend mengambil nilai maksimum, sehingga skor attempt
baru yang lebih rendah tidak menghapus mastery sebelumnya.

G1 telah diperbaiki: hasil latest deterministik, 404 saat belum ada, 400 untuk
filter invalid, dan tetap terisolasi per user/track. Daftar soal juga memakai
hubungan track yang sama dengan layanan grading. Tidak perlu migrasi database.
Gangguan POST tidak diulang otomatis: input dipertahankan, pengguna diminta
memeriksa hasil terbaru sebelum memilih mengirim attempt baru. Backend belum
menyediakan idempotency; jangan menganggap retry menjamin satu record saja.

Roadmap, materi, assessment dan credential tetap fase berikutnya.

Access dan refresh JWT disimpan **hanya di memori**, tidak di localStorage atau
sessionStorage. Reload/tab baru meminta login ulang. Request privat dengan 401
menggunakan satu refresh bersama dan retry satu kali; penolakan refresh mengakhiri
sesi, gangguan koneksi tetap dapat dicoba ulang. Logout menghapus sesi client,
bukan mencabut JWT di server. Sesi persisten memerlukan dukungan cookie HttpOnly
di backend/BFF; jangan memasukkan token ke penyimpanan browser untuk mengakalinya.

## Menjalankan web

Gunakan Node 20.19+ (baseline proyek). Jalankan backend pada port 8000 sesuai
[petunjuk backend](../back-end/README.md), lalu di terminal lain:

```powershell
cd front-end
npm ci
npm run dev
```

Buka http://127.0.0.1:3000. Next.js meneruskan `/api` ke Django tanpa mengubah
konfigurasi CORS backend. Untuk origin backend lain, salin `.env.example` ke
`.env.local` dan atur `API_PROXY_TARGET`, lalu restart Next.js.

Default `/api/v1/` menggunakan [rewrite Next.js](https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites)
ke `API_PROXY_TARGET` pada development maupun server produksi. Tetapkan target
sebelum `npm run build`; perubahan target produksi memerlukan build ulang.
Jalankan hasil produksi dengan `npm run start`. Hosting membutuhkan runtime
Next.js/Node, bukan penyajian folder statis atau `output: 'export'`.

`NEXT_PUBLIC_API_BASE_URL` opsional untuk akses langsung ke origin backend berbeda
(backend harus mengizinkan CORS). Nilainya masuk bundle saat build sesuai
[aturan environment Next.js](https://nextjs.org/docs/app/guides/environment-variables).
Jangan menaruh secret di variabel `NEXT_PUBLIC_*`. Variabel `VITE_*` tidak lagi dipakai.

Routing sekarang menggunakan `/`, `/login`, `/register`, `/profile`, `/catalog`, `/diagnostic`, dan `/diagnostic/result`, bukan
`#/...`. Gunakan Link Next.js untuk navigasi internal agar sesi di memori tetap
bertahan. Shared layout menjaga shell, sementara pages menyediakan metadata dan
konten masing-masing route. Form/sesi tetap Client Components; snapshot SSR selalu
anonim dan tidak merender profil privat. Proteksi UI dilakukan di client karena
token hanya di memori; otorisasi data tetap wajib ditegakkan Django.

## Uji frontend

```powershell
cd front-end
npm test
npm run build
```

Delapan pengujian Node mencakup payload register, login/profil, snapshot SSR anonim,
konfigurasi proxy dengan/tanpa slash akhir, login gagal,
refresh bersamaan, refresh ditolak, logout saat refresh, serta error field,
non-JSON dan jaringan. Tidak memerlukan framework test tambahan.
Enam tes tambahan fase 2 mencakup pagination/filter tanpa token publik, format
respons rusak, pembatalan request, round-trip URL semua cakupan target, parent
tidak cocok/inaktif/ID invalid, dan return-to-login tanpa open redirect.
Tiga tes fase 3 menambah validasi soal/payload/hasil, cakupan target, dan larangan
retry otomatis POST yang kehilangan respons: total 17 tes Node.
Backend assessment memiliki 12 tes, termasuk attempt berulang, skor nol,
mastery tidak menurun, tanpa XP, tie-break terbaru dan isolasi user/track.

Untuk menguji UI dengan database sementara, dari **root repo**:

```powershell
uv run --python 3.12 --with-requirements back-end/requirements.txt python front-end/tests/backend_server.py
```

Di terminal web, sebelum `npm run dev`:

```powershell
$env:API_PROXY_TARGET = 'http://127.0.0.1:8011'
npm run dev
```

Server uji memakai SQLite in-memory: berhenti berarti seluruh akun uji hilang,
database proyek tidak disentuh. Jangan gunakan server ini untuk deployment.

Untuk fase 2, tambahkan `--catalog` pada perintah server uji. Flag ini mengimpor
kurikulum repo lewat `seed_demo`, menambah fixture kosong/inaktif, dan menetapkan
dua item per halaman agar pagination teruji. Akun demo mengikuti backend:
`student` / `progressio-demo-2026`. Jangan gunakan akun/password demo di produksi.
Tanpa flag ini, server tetap kosong untuk uji registrasi atau empty state.

Smoke test fase 2 (29 September 2026) memakai Django in-memory dengan kurikulum
repo, bukan mock katalog. Terverifikasi pada dev dan server produksi: pagination
dua item per halaman, pilihan bertingkat, target career track/skill (semua cakupan
diuji otomatis), prasyarat skill,
reset child saat parent berubah, Back, dan pemulihan URL lengkap setelah reload
lalu login. URL dengan skill dari competency lain ditolak. Backend mati memicu
error/retry; retry berhasil memuat empty state saat backend kosong dihidupkan.
Clipboard ditolak dalam browser uji dan fallback salin bilah alamat tampil.
Layout diperiksa pada 375 x 812 dan 812 x 375 tanpa overflow horizontal;
reduced-motion aktif menghasilkan transisi 0s. Tidak ada error hidrasi pada alur
normal. Uji ini belum mencakup diagnostic atau penerbitan credential.

Smoke test fase 3 (29 September 2026) memakai kurikulum/Django in-memory:
target -> diagnostic, 15 inline error dengan fokus ringkasan ketika belum diisi,
attempt “Belum tahu” bernilai 0, attempt kedua bernilai 100 dan hasil terbaru
menunjukkan attempt kedua. Pada build produksi, reload -> login memulihkan URL
hasil dan skor dari backend. Track tanpa soal dan tanpa attempt menampilkan
empty state berbeda. Hasil diperiksa pada lebar 375 px dan landscape 812 px;
tidak ada overflow horizontal, reduced-motion menghasilkan transisi 0s.
Tidak ditemukan error browser pada alur normal. Koneksi POST hilang diuji
otomatis dengan respons terkontrol, bukan gangguan jaringan browser nyata.
Smoke test browser fase 1 pada 29 September 2026 memverifikasi daftar -> masuk -> profil,
muat ulang profil, logout/proteksi route, password salah, konfirmasi berbeda,
username duplikat, kegagalan backend dengan isian tetap tersimpan, dan lebar
mobile 375 px tanpa overflow horizontal.
Refresh token diuji otomatis dengan respons terkontrol, bukan menunggu expiry
30 menit di browser. Ini belum merupakan uji seluruh perjalanan Progressio.

Migrasi Next.js juga diuji pada tanggal yang sama: dev server berhasil menjalankan
register/login/profil/logout, login gagal dengan fokus error dan isian tetap ada,
proteksi `/profile/`, serta layout mobile 375 px. Server hasil `npm run build` +
`npm run start` berhasil menjalankan login dan navigasi profil tanpa kehilangan
sesi atau error hidrasi. Reload `/profile` kembali ke login. Halaman tak dikenal
menghasilkan HTTP 404; HTML server tidak berisi identitas akun yang login.
Proxy diuji dengan `career-tracks/?page=1` (200 JSON tanpa redirect) dan `auth/me`
tanpa token (401). Database sementara tidak berisi katalog, sehingga hasil list
kosong bukan uji alur pemilihan target. Slash akhir dipertahankan oleh rewrite;
jangan menormalisasi semua endpoint Django ke satu bentuk URL.

## Struktur dan fase berikutnya

- `src/app/`: layout, pages, metadata dan halaman 404 App Router.
- `src/App.jsx`: shell dan komponen interaktif auth/workspace.
- `src/Catalog.jsx`: UI pilihan bertingkat, detail dan ringkasan target.
- `src/catalog.js`: pagination, validasi URL dan relasi target.
- `src/Diagnostic.jsx` dan `src/diagnostic.js`: kuis, hasil terbaru dan kontrak diagnostic.
- `src/navigation.js`: tujuan login internal yang aman.
- `src/api.js`: API client, sesi dan refresh terkoordinasi.
- `src/styles.css`: identitas visual dan responsivitas.
- `next.config.mjs`: rewrite API ke Django.
- `tests/`: tes client dan backend sementara untuk smoke test.

Fase 3 menyambungkan diagnostic dan hasil titik awal serta menyelesaikan G1.
Langkah berikutnya adalah roadmap dari target, hasil dan prasyarat; materi,
assessment dan credential tetap fase lanjutan.
Kontrak backend dan gap integrasi tetap tersedia di [API_CONTRACT.md](API_CONTRACT.md).

## Probe fase 0

Jalankan probe dari root repo dengan environment backend yang sehat:

```powershell
python front-end/check_api_contract.py
```

Alternatif dengan uv dan Python 3.12:

```powershell
uv run --python 3.12 --with-requirements back-end/requirements.txt python front-end/check_api_contract.py
```

Probe memakai SQLite in-memory, mengimpor kurikulum, membuat akun sementara,
memeriksa respons HTTP dan OpenAPI, lalu melaporkan gap yang diketahui.
Tidak menggunakan database proyek atau layanan AI/blockchain eksternal.
Assertion gagal menghasilkan exit code nonzero; baris `OBSERVED`/`SCHEMA GAP`
adalah hasil audit yang harus ditinjau, bukan klaim bahwa fitur tersebut sudah benar.
