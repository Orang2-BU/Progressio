# Progressio frontend

Fase 0: kontrak backend dan gap integrasi tersedia di [API_CONTRACT.md](API_CONTRACT.md).
Belum ada framework atau UI web di folder ini. Aplikasi Flutter berada di `../Mobile/`.

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
