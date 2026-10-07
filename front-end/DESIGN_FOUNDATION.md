# Fondasi web Progressio v3.1

Acuan: Palette v3, komponen dan ikon v3, dashboard v3, serta login/register desktop di project Canvas Progressio Learning Platform. CSS biasa dimuat oleh `src/app/layout.jsx`: `src/styles.css` berisi token awal dan aturan halaman yang sudah ada; `src/foundation.css` menimpa aturan bersama untuk shell, auth, kontrol, dan komponen v3.1. Halaman baru sebaiknya memberi prefix kelasnya sendiri agar tidak mengubah halaman lain.

## Token dan tema

Gunakan variabel CSS di `src/styles.css` dan `src/foundation.css`: `--page`, `--surface`, `--soft`, `--ink`, `--muted`, `--line`, `--lime`, `--lime-hover`, `--lime-edge`, `--green-text`, `--sky`, `--violet`, `--amber`, `--coral`. Empat aksen terakhir juga memiliki pasangan `-edge` dan `-tint`; lime memakai `--selected` sebagai tint. Tema gelap mengikuti `prefers-color-scheme: dark` dan memberi `--green-text` nilai `#cfe79a`. Neon `#b5f942` dipakai hanya oleh `.brand-mark`. Tipografi memakai Segoe UI, kontainer 1360 px, gutter 20/32/40 px, dan radius kartu 16/24 px.

## Komponen React

Ekspor dari `src/ui.jsx`:

| Komponen | Pemakaian |
|---|---|
| `Icon` | `<Icon name="target" size={20} />`; default dekoratif, `label` untuk ikon yang membawa makna sendiri. Nama tersedia pada `paths` di file itu. Semua stroke `currentColor`. |
| `Button` | `<Button href="/catalog">Pilih target</Button>` atau `<Button variant="secondary" onClick={...}>Kembali</Button>`. Class `.button.primary` dan `.button.secondary` juga dapat dipakai pada elemen HTML/Next Link yang sudah ada. |
| `Notice` | `<Notice tone="warning" title="Periksa jawaban">...</Notice>`. Tone: success, info, warning, error. Judul standar selalu menuliskan status. |
| `StatusBadge` | `<StatusBadge tone="success">Selesai</StatusBadge>`; teks status wajib terlihat. Tone sama dengan `Notice`. |
| `ProgressBar` | `<ProgressBar value={done} max={total} label="Soal dijawab" />`; nilai dijepit ke rentang 0–max dan diumumkan sebagai progressbar. Saat total belum tersedia, angka kemajuan tidak diumumkan sebagai angka final. Tampilkan teks jumlah di dekat bar seperti pada `FocusLayout`. |
| `DifficultyTag` | `<DifficultyTag level={skill.difficulty} />`; menerima beginner/intermediate/advanced atau Pemula/Menengah/Mahir, tanpa nilai rekaan. |
| `JourneyTracker` | `<JourneyTracker statuses={['complete','current','upcoming','locked','locked']} />`; urutan Target, Diagnostic, Roadmap, Study, Bukti. Setiap langkah menampilkan label status. Status harus berasal dari data/alur nyata, bukan selalu menganggap langkah sebelumnya selesai. Pada viewport kecil, tracker dapat digulir mendatar tanpa menggulir halaman. |
| `EmptyState` | `<EmptyState icon="target" title="Belum ada target" action={<Button href="/catalog">Pilih target</Button>}>Pilih target untuk mulai.</EmptyState>` |
| `LoadingState` | `<LoadingState>Memuat target…</LoadingState>`; teks diumumkan sebagai status. |

## Shell

`WorkspaceLayout` dari `src/App.jsx` memasang sidebar empat menu pada dashboard, katalog, hasil Diagnostic, Roadmap, Study, Assessment, Credential dan profil. `aria-current="page"` hanya diberikan pada path persis `/`, `/catalog`, `/credentials`, atau `/profile`. Rute `/verify/[id]` memakai pembungkus publik tanpa sidebar. `App` tetap mengurus auth guard, skip link, fokus saat rute berubah, logout, dan safe next redirect.

Rute soal `/diagnostic` memakai `FocusLayout` dari `src/App.jsx`, yang menampilkan tombol kembali ke target, progres jawaban, dan konten dalam kolom terpusat. `App` tidak menampilkan topbar dan footer workspace pada path tersebut. Contoh: `<FocusLayout exitHref={catalogHref} completed={answeredCount} total={questionCount}><section className="workspace-content diagnostic-content">...</section></FocusLayout>`. Letakkan tombol submit form di `.focus-actions` bila memerlukan action bar lengket. `/diagnostic/result` tetap memakai `WorkspaceLayout`.

Topbar menampilkan inisial dan peran dari sesi. Chip streak, level, lencana, heatmap, dan statistik komunitas belum ditampilkan karena API belum menyediakan nilainya. Total XP tersedia melalui `GET progress`, tetapi fondasi topbar tidak melakukan request tambahan; tiket dashboard dapat menampilkannya dari respons server.
