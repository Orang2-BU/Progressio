# Changelog

## Unreleased

- Turbopack root is pinned to `front-end`, so the unrelated repository lockfile cannot be mistaken for this app's workspace root.
- Status credential issued yang belum valid atau belum terkonfirmasi integritasnya kini tetap ditampilkan sebagai terbit dengan alasan integritas server, bukan keliru diberi label Draft.
- Assessment, credential, dan verifikasi publik kini memakai pola visual web v3.1 dengan status, skor, threshold lulus, snapshot rubric/standar, dan evidence dari server; draft/mock tetap jelas bukan credential final.
- Daftar credential mendukung filter status dan competency yang tersedia di API, sementara tautan verifikasi publik dapat disalin dengan fallback clipboard.
- Dashboard dan profil akun kini merangkum XP serta completion dari server, menampilkan CTA target saat URL belum memilih target, dan menandai fitur profil yang belum didukung sebagai SEGERA.
- Logout lokal dari topbar dan profil tidak lagi menerima query URL sebagai bukti sukses, serta memberi tahu bahwa pencabutan refresh token server belum dikonfirmasi.
