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

Pada akhir fase 3, roadmap, materi, assessment dan credential masih fase berikutnya.

## Status fase 4 — roadmap personal

`/roadmap` dibuka dari katalog atau hasil diagnostic, dengan query target yang
sama. Career track, competency dan skill divalidasi lewat katalog; request API
memakai tepat satu **slug dari server**, bukan ID atau slug yang dipercaya dari
URL. Resolver target sekarang digunakan bersama oleh diagnostic dan roadmap.

Roadmap menampilkan urutan skill/prasyarat dari server, estimasi belajar tersisa,
mastery tersimpan, langkah bagian target versus prasyarat target, serta skill
yang sudah cukup untuk jalur ini. Prasyarat memakai details/summary native yang
dapat dibuka lewat keyboard. Tidak ada library diagram atau mesin roadmap baru.
Loading, error/retry, target invalid dan roadmap tanpa langkah dibedakan.
Track tanpa skill mendapat error backend, bukan dianggap target sudah tercapai.

Diagnostic belum wajib. Tanpa progress backend memakai mastery 0; setelah
diagnostic, roadmap otomatis memakai mastery yang diperbarui server. Mastery
dapat pula berasal dari aktivitas belajar/assessment. Attempt terbaru yang
lebih rendah tidak menurunkan mastery sebelumnya, jadi roadmap tidak selalu
mengikuti skor attempt terakhir. GET/refresh roadmap tidak mengubah mastery/XP.

G6 dijelaskan eksplisit di UI dan diuji pada 69.9/70/84.9/85: **cukup untuk
roadmap** menggunakan 70, sementara learning-path **mastered** menggunakan 85.
Kebijakan backend tidak diubah. Keduanya bukan evidence assessment atau bukti
kelayakan credential. Jika semua langkah kosong, UI tetap menyatakan kebutuhan
evidence, bukan menampilkan tombol penerbitan credential.

URL dapat dibuka kembali setelah login ulang. Roadmap dihitung saat dimuat,
bukan snapshot/rencana yang disimpan lintas perangkat. Materi, assessment dan
credential tetap fase lanjutan; tidak ada mutasi completion pada fase ini.

## Status fase 5 — materi, checkpoint dan completion

`/study?track={id}&learn={skill_id}` membuka materi suatu skill dengan konteks
target tetap di query. Roadmap memberi tautan setiap langkah; katalog memberi
tautan skill pilihan, termasuk untuk belajar ulang setelah roadmap kosong.
Skill materi harus berada pada career track aktif target. Semua halaman
pagination lesson dan study plan dimuat; materi kosong dan materi tanpa study
plan dibedakan. Materi tetap di penerbit, tidak di-crawl, disalin, atau di-embed.

UI menampilkan provider, lisensi yang dicatat, status verifikasi lisensi,
attribution dan status tautan terakhir. Paket kurikulum saat ini belum melakukan
verifikasi lisensi satu per satu: tidak ada klaim “aman disalin”. URL hanya
HTTP(S) tanpa credentials; URL kosong/unsafe dan status broken tidak menjadi
tautan aktif. Link eksternal memakai tab baru + noopener/noreferrer. Pemeriksaan
ini bukan pengecekan reachability sumber saat ini atau audit lisensi hukum.

Study plan memuat instruksi, bagian sumber, estimasi dan checkpoint teks singkat.
Checkpoint dinilai server tanpa kunci jawaban di client. HTTP 200 dengan correct
false tetap berarti jawaban belum sesuai. Feedback tidak persisten dan tidak
memberi completion, XP, atau evidence credential; reload menghapus feedback.

G3 diselesaikan untuk status completion: `progress` kini mengirim
`completed_lesson_ids` milik user. Badge/tombol berasal dari ID tersebut, bukan
mastery atau jumlah completion saja. Completion adalah pernyataan eksplisit
“saya selesai mempelajari”, bukan efek membuka link atau menjawab checkpoint.
Reward lama backend tetap +50 XP per lesson baru dan mastery belajar maksimal
70, tanpa menurunkan mastery yang lebih tinggi. Transaksi dan lock user pada
database yang mendukung row locking menjaga completion/reward bersama; rollback
dan replay sequential diuji. Ini bukan benchmark konkurensi PostgreSQL.

Setelah POST, progress diambil ulang. Network/5xx/respons invalid tidak diulang
otomatis; progress diberi status belum pasti dan tombol completion dinonaktifkan
sampai pengguna memperbarui progress. Jawaban checkpoint tetap ada saat gagal.
Completion tersimpan di backend dan kembali setelah reload/login; target hanya
di URL. Tidak ada migrasi database atau dependensi runtime baru.

Assessment dan credential tetap fase berikutnya. Selesai materi/70 mastery tidak
membuktikan assessment lulus atau kelayakan credential (backlog G5 masih ada).

Access dan refresh JWT disimpan **hanya di memori**, tidak di localStorage atau
sessionStorage. Reload/tab baru meminta login ulang. Request privat dengan 401
menggunakan satu refresh bersama dan retry satu kali; penolakan refresh mengakhiri
sesi, gangguan koneksi tetap dapat dicoba ulang. Logout menghapus sesi client,
bukan mencabut JWT di server. Sesi persisten memerlukan dukungan cookie HttpOnly
di backend/BFF; jangan memasukkan token ke penyimpanan browser untuk mengakalinya.

## Status fase 6 — assessment sampai verifikasi publik

`/assessment` dibuka dari materi dengan konteks target/skill yang sama. UI memuat
tujuan, evidence yang diminta, kriteria, rubrik publik tanpa answer key, dan soal
quiz. Semua pilihan quiz wajib; project/challenge mengirim isi evidence teks/kode
dan tautan HTTP(S) opsional. Tidak ada upload, crawler repository, atau eksekusi kode.
Penilai mock kini membaca evidence `text` maupun `code`. AI hanya menilai isi yang
dikirim, bukan membuktikan repository yang belum diambil.

Hasil dan riwayat milik akun dibaca dari GET submission, termasuk setelah reload
dan login ulang. URL `submission` menunjuk hasil tertentu, bukan latest. Snapshot
menyimpan threshold, versi, kriteria, dan provenance evaluator (`rules`, `mock`,
`openai`, atau `mock-fallback`). Submission lama tetap dapat dibaca tetapi tanpa
provenance tidak memenuhi syarat credential baru.

Form memakai request UUID dan lock submit. Recovery GET memakai request ID;
retry eksplisit memakai payload/ID yang sama, sehingga submission dan XP tidak
ganda. ID yang dipakai untuk payload berbeda ditolak. Kegagalan provider/score
invalid rollback hasil dan reward; pesan tidak membocorkan detail provider.
Tidak ada retry otomatis untuk network/5xx. Isian tetap ada dan dikunci ketika
status belum pasti; reload/navigasi meninggalkan form menghapus isian lokal.
Client lama tanpa request ID masih didukung, tetapi tidak mendapat jaminan replay.
Penilaian tetap sinkron; row lock per-user bukan uji beban/konkurensi PostgreSQL.

`/credentials?claim={competency_id}` membaca eligibility tanpa mutasi. Semua skill
competency diwajibkan punya assessment lulus pada versi kurikulum aktif; skor
credential berasal dari rata-rata skor assessment yang dinormalisasi, bukan
mastery diagnostic/lesson. Evidence reviewed/non-mock diprioritaskan. Missing skill
memberi tautan assessment. Target skill tetap menghasilkan credential competency,
bukan credential skill tunggal.

Final memerlukan track aktif dengan versi/schema dan metadata status `reviewed`,
evidence grading `reviewed`, evaluator rules/OpenAI tanpa fallback mock, serta
provider proof `http` yang mengonfirmasi proof. Kurikulum repo masih draft: hasil
lulus hanya memungkinkan **draft demo** lewat pilihan eksplisit `demo: true`.
Draft tidak di-anchor, `issued_at` null dan `is_valid` false. Repeat issuance untuk
versi/evidence/mode sama mengembalikan record yang sama; versi/evidence baru bisa
membuat credential lain. Evidence tiap skill dan standar disnapshot; hash baru
meliputi standar/provenance. Tidak ada promosi otomatis draft menjadi final.

`/credentials?id={uuid}` menampilkan detail privat, daftar memakai paging server.
`/verify/{uuid}` publik tanpa login, menampilkan standar saat dibuat, evidence,
status valid/revoked/proof missing, dan label demo/legacy dengan jujur. Snapshot
publik tidak mengekspos email atau isi mentah submission. Proof tidak membuktikan
bahwa situs/repository eksternal masih sama atau bahwa audit manusia dilakukan.

Migrasi baru `assessments/0006_submission_recovery` diperlukan. Dari root:

```powershell
$env:DB_ENGINE = 'sqlite' # atau konfigurasi database deployment milikmu
uv run --python 3.12 --with-requirements back-end/requirements.txt python back-end/manage.py migrate
uv run --python 3.12 --with-requirements back-end/requirements.txt python back-end/manage.py import_curriculum
```

Import memperbarui review metadata grading dari paket; jangan mengubah draft
menjadi reviewed hanya untuk melewati gate. Migrasi/import database proyek belum
dijalankan oleh agent; pengujian memakai database sementara.

Fase frontend 0–6 tersambung untuk MVP/demo. Kesiapan produksi masih membutuhkan
review kurikulum/lisensi, uji provider nyata, cookie HttpOnly untuk sesi persisten,
dan operational/security/load testing. Anchoring eksternal belum memiliki outbox:
timeout setelah provider menerima proof dapat meninggalkan proof orphan saat DB
rollback; produksi memerlukan recovery/reconciliation provider, bukan retry buta.

## Menjalankan web (development)

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

Routing sekarang menggunakan `/`, `/login`, `/register`, `/profile`, `/catalog`, `/diagnostic`, `/diagnostic/result`, `/roadmap`, dan `/study`, bukan
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

`npm ci` memasang versi yang terkunci di `package-lock.json` dan membutuhkan
Node `>=20.19.0`. Workflow web CI menjalankan instalasi bersih, tes, build, lalu
probe kontrak dengan Python 3.12 dalam virtualenv job dan dependency dari
`back-end/requirements.txt`.

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
Tiga tes fase 4 menambah target slug/routing, validasi urutan dan ringkasan
roadmap, empty route, GET berautentikasi/read-only, error dan cancellation:
total 20 tes Node. Backend roadmap memiliki 17 tes; digabung assessment menjadi
29 tes, termasuk diagnostic -> roadmap, isolasi user dan ambang 70/85.
Lima tes fase 5 menambah URL aman, pagination materi/study plan, parent track,
empty/unplanned content, progress IDs, payload checkpoint, false feedback,
completion tanpa body dan lost response: total 25 tes Node.
Learning + assessment + credential memiliki 55 tes, termasuk rollback reward,
completion IDs per-user, completion tidak disimpulkan dari diagnostic, dan
checkpoint tidak mengubah XP/completion. Probe API sekarang memeriksa 26 request
serta schema checkpoint; schema filter learning-path tetap backlog G10.

Jalankan tes backend terkait dari root repo tanpa memakai database proyek:

```powershell
$env:DB_ENGINE = 'sqlite'
uv run --python 3.12 --with-requirements back-end/requirements.txt python back-end/manage.py test apps.learning apps.assessments apps.credentials
```

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

Untuk fase 2–5, tambahkan `--catalog` pada perintah server uji. Flag ini mengimpor
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

Smoke test fase 4 (29 September 2026), dengan Django/kurikulum in-memory:
target career track -> 7 langkah, competency API Development -> 6 langkah,
skill API Input Validation -> 6 langkah dengan 5 prasyarat sebelum target.
Diagnostic 100 -> hasil -> roadmap yang sama menjadi 0 langkah tanpa klaim
credential. Prasyarat dapat dibuka dengan Enter. Layout 375 x 812 dan landscape
812 x 375 tidak overflow; reduced-motion menghasilkan transisi 0s. Build
produksi + reload -> login memulihkan URL skill lengkap dan hasil roadmap.
Backend dihentikan -> error; dihidupkan kembali dengan database uji baru ->
retry berhasil dan memakai progress baru, bukan hasil client lama. Track tanpa
skill menampilkan error katalog. Tidak ada error browser pada alur normal.

Smoke test fase 5 (29 September 2026) dengan Django in-memory + kurikulum repo:
roadmap -> HTTP Messages and Semantics memuat 3 lesson dan 3 checkpoint dengan
pagination 2 item. Provider/lisensi belum terverifikasi ditampilkan; blank answer
memfokuskan error summary, jawaban salah/benar memiliki feedback berbeda dan
tidak menambah XP. Completion satu lesson menghasilkan 1/3, 50 XP dan mastery
23.3 dari server; tombol lesson selesai disabled. Build produksi + reload/login
memulihkan URL dan completion, tetapi feedback checkpoint hilang. Link sumber
diperiksa sebagai HTTP(S) dengan noopener/noreferrer, tanpa menguji situs penerbit
atau memverifikasi lisensinya. Tampilan 375 px, landscape dan reduced-motion
diperiksa tanpa overflow; tidak ada error browser pada alur normal produksi.
Backend mati saat checkpoint/completion mempertahankan jawaban dan menandai
progress belum pasti; restart memakai database uji baru + refresh memulihkan
progress terbaru dan tombol, bukan completion client lama. Empty/unplanned content
dan unsafe URLs diuji otomatis; belum melalui smoke test browser tersendiri.
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
- `src/Roadmap.jsx` dan `src/roadmap.js`: roadmap dan validasi kontrak server.
- `src/Study.jsx` dan `src/study.js`: materi, checkpoint dan completion berbasis server.
- `src/navigation.js`: tujuan login internal yang aman.
- `src/api.js`: API client, sesi dan refresh terkoordinasi.
- `src/styles.css`: identitas visual dan responsivitas.
- `next.config.mjs`: rewrite API ke Django.
- `tests/`: tes client dan backend sementara untuk smoke test.

Fase 0–6 menyambungkan target, diagnostic, roadmap, materi, assessment/evidence,
hasil persisten, draft demo, dan verifikasi publik. Langkah berikutnya adalah
review standar dan kesiapan produksi, bukan menambah fase frontend baru.
Kontrak backend dan gap integrasi tetap tersedia di [API_CONTRACT.md](API_CONTRACT.md).

### Verifikasi fase 6

29 tes Node, seluruh aplikasi Django (129 tes), dan probe 31 request API menguji
replay/recovery, owner isolation, score/provenance snapshot, invalid evidence,
rollback evaluator/proof failure, demo gate, issuance replay dan tamper criteria.
`makemigrations --check --dry-run` tidak menemukan perubahan model yang belum
dimigrasikan. Build Next.js berhasil untuk route baru, termasuk verifikasi dinamis.

Browser dev dan produksi dengan Django in-memory (29 September 2026): materi ->
quiz, blank submit memfokuskan summary dengan 6 inline error, quiz lulus 100,
evidence mock pertama 20.6 lalu attempt baru 100, missing skill memblokir demo,
tautan assessment skill hilang, draft dengan evidence kedua skill dan snapshot,
serta public verification tanpa login menampilkan draft invalid/proof missing.
Backend dihentikan saat submit: evidence/request ID tetap; GET recovery setelah
restart DB uji baru menunjukkan belum ada, retry eksplisit menyimpan satu hasil.
Ini bukan simulasi provider nyata yang timeout setelah menyimpan hasil; lost-response
recovery/replay diuji otomatis. Login ulang pada build produksi memulihkan URL
credential dan data server. Public verification diperiksa pada 375 px/landscape
tanpa overflow; snapshot mobile diinspeksi visual. Tidak ada runtime error aplikasi
pada sesi produksi bersih; satu error evaluasi CLI karena quoting bukan error app.
Tidak ada klaim reachability/lisensi sumber, provider nyata, audit manusia, load
testing atau deployment produksi. Semua server/database uji bersifat disposable.

## Probe fase 0

Jalankan probe dari root repo dengan environment backend yang sehat:

```powershell
$python = "back-end/.venv/Scripts/python.exe" # venv baru dari back-end/README.md
& $python front-end/check_api_contract.py
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
