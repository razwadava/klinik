# Klinik PMI - REST API (Flask + Supabase + Vercel)

Struktur:
- app.py            -> REST API Flask (Vercel mendeteksi otomatis)
- public/index.html -> tampilan client (dilayani Vercel)
- requirements.txt
- supabase.sql      -> opsional, buat tabel manual
- .gitignore

## Deploy
1. Supabase: buat project, simpan password database.
2. SQL Editor: jalankan isi supabase.sql.
3. Connect > Transaction pooler (port 6543) > salin connection string,
   ganti [YOUR-PASSWORD] dengan password kamu.
4. Upload folder ini ke GitHub.
5. Vercel: Add New > Project > pilih repo > (sebelum Deploy) tambah
   Environment Variable: DATABASE_URL = connection string tadi > Deploy.
6. Buka https://NAMA-PROJECT.vercel.app

## Tes lokal (opsional)
    pip install -r requirements.txt
    # Windows (CMD):   set DATABASE_URL=postgresql://...
    # Linux/Mac:       export DATABASE_URL="postgresql://..."
    python app.py      # buka http://localhost:5000

## Tes via curl
    curl https://NAMA-PROJECT.vercel.app/api/pasien
    curl -X POST https://NAMA-PROJECT.vercel.app/api/pasien -H "Content-Type: application/json" -d '{"no_rm":"RM001","nama":"Budi","umur":30}'
    curl -X PUT https://NAMA-PROJECT.vercel.app/api/pasien/1 -H "Content-Type: application/json" -d '{"no_rm":"RM001","nama":"Budi S","umur":31}'
    curl -X DELETE https://NAMA-PROJECT.vercel.app/api/pasien/1
