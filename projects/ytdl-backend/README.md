# YTDL Backend — Setup Guide

## 1. Upload ke server Debian lo

```bash
# Di server Debian lo
mkdir -p /var/www/ytdl-backend
cd /var/www/ytdl-backend
```

Upload semua file di folder `ytdl-backend/` ini ke sana.

---

## 2. Install dependencies

```bash
# Install ffmpeg (wajib untuk konversi audio)
sudo apt update
sudo apt install ffmpeg python3 python3-pip python3-venv -y

# Buat virtual environment
cd /var/www/ytdl-backend
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

---

## 3. Jalankan sebagai service (auto-start)

```bash
# Copy service file
sudo cp ytdl.service /etc/systemd/system/ytdl.service

# Enable & start
sudo systemctl daemon-reload
sudo systemctl enable ytdl
sudo systemctl start ytdl

# Cek status
sudo systemctl status ytdl
```

---

## 4. Setup Nginx reverse proxy

Buka config Nginx lo:
```bash
sudo nano /etc/nginx/sites-available/ihir.my.id
```

Tambahkan isi `nginx-snippet.conf` ke dalam block `server { ... }` yang ada,
sebelum tanda `}` penutup.

Lalu reload Nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 5. Test

Dari browser atau terminal:
```bash
# Test info endpoint
curl "https://ihir.my.id/api/info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Harusnya return JSON berisi title, uploader, dll
```

---

## Struktur file server

```
/var/www/ytdl-backend/
├── app.py
├── requirements.txt
├── ytdl.service
├── nginx-snippet.conf
├── venv/
└── downloads/       ← file temp, auto cleanup setelah 10 menit
```

---

## Catatan

- Backend jalan di port `5000`, diakses lewat Nginx di path `/api/`
- File download otomatis dihapus setelah 10 menit
- CORS sudah di-set hanya izinkan `https://ihir.my.id`
