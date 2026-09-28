-- Jalankan di Supabase: menu SQL Editor > New query > paste > Run
-- (app.py juga membuat tabel ini otomatis, file ini opsional)
CREATE TABLE IF NOT EXISTS pasien (
  id SERIAL PRIMARY KEY,
  no_rm VARCHAR(30) UNIQUE NOT NULL,
  nama VARCHAR(100) NOT NULL,
  umur INT NULL,
  jenis_kelamin VARCHAR(20) NULL,
  golongan_darah VARCHAR(3) NULL,
  keluhan VARCHAR(255) NULL,
  tanggal_kunjungan DATE NULL
);
