# Progressio frontend

Frontend web React + Vite. Aplikasi Flutter tetap berada di `../Mobile/`.

## Status fase 1

Fondasi web tersedia: halaman daftar/masuk, ringkasan workspace, profil baca saja,
logout, proteksi halaman, validasi form, loading/error, dan layout responsif.
Registrasi dan profil menggunakan API Django, bukan data dummy. Role student dan
recruiter mengikuti backend; menu belajar/assessment belum diimplementasikan.
Warna mengikuti identitas aplikasi Mobile; form memakai label, fokus keyboard,
ringkasan error dan pesan status yang dapat diakses.

Access dan refresh JWT disimpan **hanya di memori**, tidak di localStorage atau
sessionStorage. Reload/tab baru meminta login ulang. Request privat dengan 401
menggunakan satu refresh bersama dan retry satu kali; penolakan refresh mengakhiri
sesi, gangguan koneksi tetap dapat dicoba ulang. Logout menghapus sesi client,
bukan mencabut JWT di server. Sesi persisten memerlukan dukungan cookie HttpOnly
di backend/BFF; jangan memasukkan token ke penyimpanan browser untuk mengakalinya.

## Menjalankan web

Gunakan Node 20.19+ yang didukung Vite. Jalankan backend pada port 8000 sesuai
[petunjuk backend](../back-end/README.md), lalu di terminal lain:

```powershell
cd front-end
npm ci
npm run dev
```

Buka http://127.0.0.1:5173. Vite meneruskan `/api` ke Django tanpa mengubah
konfigurasi CORS backend. Untuk origin backend lain, salin `.env.example` ke
`.env.local` dan atur `API_PROXY_TARGET`, lalu restart Vite.

`VITE_API_BASE_URL` dapat diatur saat build jika API produksi berada di origin
berbeda (backend harus mengizinkan CORS). Default `/api/v1/` memerlukan reverse
proxy `/api` di hosting produksi. `npm run preview` hanya menyajikan hasil build,
bukan proxy Django yang dikonfigurasi untuk development. Jangan menaruh secret
di variabel `VITE_*` karena nilainya masuk bundle publik.

## Uji fase 1

```powershell
cd front-end
npm test
npm run build
```

Enam pengujian Node mencakup payload register, login/profil, login gagal,
refresh bersamaan, refresh ditolak, logout saat refresh, serta error field,
non-JSON dan jaringan. Tidak memerlukan framework test tambahan.

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
Smoke test browser pada 29 September 2026 memverifikasi daftar -> masuk -> profil,
muat ulang profil, logout/proteksi route, password salah, konfirmasi berbeda,
username duplikat, kegagalan backend dengan isian tetap tersimpan, dan lebar
mobile 375 px tanpa overflow horizontal.
Refresh token diuji otomatis dengan respons terkontrol, bukan menunggu expiry
30 menit di browser. Ini belum merupakan uji seluruh perjalanan Progressio.

## Struktur dan fase berikutnya

- `src/App.jsx`: halaman dan navigasi hash sederhana.
- `src/api.js`: API client, sesi dan refresh terkoordinasi.
- `src/styles.css`: identitas visual dan responsivitas.
- `tests/`: tes client dan backend sementara untuk smoke test.

Fase 2 menyambungkan katalog/target dan alur pengukuran sesuai plan; roadmap,
materi, assessment dan credential belum dianggap selesai oleh fase ini.
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
