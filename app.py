# SERVER (REST API + PostgreSQL Supabase) - siap deploy ke Vercel
import os
import psycopg2
import psycopg2.extras
from psycopg2 import errors
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Isi dari Supabase: Connect > Transaction pooler (port 6543)
DATABASE_URL = os.environ.get("DATABASE_URL")

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
FIELDS = ["no_rm", "nama", "umur", "jenis_kelamin", "golongan_darah", "keluhan", "tanggal_kunjungan"]

_table_ready = False


def get_db():
    if not DATABASE_URL:
        raise RuntimeError("Environment variable DATABASE_URL belum diisi")
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=10,
                            cursor_factory=psycopg2.extras.RealDictCursor)
    conn.autocommit = True
    return conn


def ensure_table():
    """Buat tabel jika belum ada (aman dipanggil berulang)."""
    global _table_ready
    if _table_ready:
        return
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS pasien (
                id SERIAL PRIMARY KEY,
                no_rm VARCHAR(30) UNIQUE NOT NULL,
                nama VARCHAR(100) NOT NULL,
                umur INT NULL,
                jenis_kelamin VARCHAR(20) NULL,
                golongan_darah VARCHAR(3) NULL,
                keluhan VARCHAR(255) NULL,
                tanggal_kunjungan DATE NULL)""")
        _table_ready = True
    finally:
        conn.close()


def run(sql, params=(), fetch=False):
    ensure_table()
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall() if fetch else None
            return cur.rowcount, rows
    finally:
        conn.close()


def clean(v):
    return None if v in ("", None) else v  # string kosong -> NULL (penting untuk kolom DATE/INT)


def ser(r):
    return {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in r.items()}


# ---------- Penanganan error umum (selalu balas JSON) ----------
@app.errorhandler(psycopg2.OperationalError)
def db_unreachable(e):
    return jsonify({"error": "Tidak bisa terhubung ke database", "detail": str(e)}), 503


@app.errorhandler(psycopg2.DataError)
def bad_data(e):
    return jsonify({"error": "Format data tidak valid (cek umur / tanggal)"}), 400


@app.errorhandler(RuntimeError)
def config_error(e):
    return jsonify({"error": str(e)}), 500


# ---------- Halaman utama (lokal). Di Vercel, public/index.html dilayani otomatis ----------
@app.get("/")
def index():
    return send_from_directory(PUBLIC_DIR, "index.html")


# GET - semua pasien
@app.get("/api/pasien")
def list_pasien():
    q = request.args.get("q", "")
    _, rows = run("SELECT * FROM pasien WHERE nama ILIKE %s ORDER BY id DESC", (f"%{q}%",), fetch=True)
    return jsonify([ser(r) for r in rows])


# GET - satu pasien
@app.get("/api/pasien/<int:pid>")
def get_pasien(pid):
    _, rows = run("SELECT * FROM pasien WHERE id=%s", (pid,), fetch=True)
    if not rows:
        return jsonify({"error": "Pasien tidak ditemukan"}), 404
    return jsonify(ser(rows[0]))


# POST - tambah
@app.post("/api/pasien")
def add_pasien():
    d = request.get_json(silent=True) or {}
    if not d.get("no_rm") or not d.get("nama"):
        return jsonify({"error": "no_rm dan nama wajib diisi"}), 400
    try:
        _, rows = run(f"INSERT INTO pasien ({','.join(FIELDS)}) VALUES ({','.join(['%s'] * len(FIELDS))}) RETURNING id",
                      [clean(d.get(f)) for f in FIELDS], fetch=True)
        return jsonify({"message": "Pasien ditambahkan", "id": rows[0]["id"]}), 201
    except errors.UniqueViolation:
        return jsonify({"error": "No. RM sudah terdaftar"}), 409


# PUT - update
@app.put("/api/pasien/<int:pid>")
def update_pasien(pid):
    d = request.get_json(silent=True) or {}
    if not d.get("no_rm") or not d.get("nama"):
        return jsonify({"error": "no_rm dan nama wajib diisi"}), 400
    try:
        n, _ = run(f"UPDATE pasien SET {','.join(f + '=%s' for f in FIELDS)} WHERE id=%s",
                   [clean(d.get(f)) for f in FIELDS] + [pid])
    except errors.UniqueViolation:
        return jsonify({"error": "No. RM sudah dipakai pasien lain"}), 409
    if n == 0:
        return jsonify({"error": "Pasien tidak ditemukan"}), 404
    return jsonify({"message": "Data pasien diperbarui"})


# DELETE - hapus
@app.delete("/api/pasien/<int:pid>")
def delete_pasien(pid):
    n, _ = run("DELETE FROM pasien WHERE id=%s", (pid,))
    if n == 0:
        return jsonify({"error": "Pasien tidak ditemukan"}), 404
    return jsonify({"message": "Pasien dihapus"})


if __name__ == "__main__":
    # Hanya untuk tes lokal. Di Vercel, variabel `app` dijalankan otomatis.
    app.run(host="0.0.0.0", port=5000, debug=False)
