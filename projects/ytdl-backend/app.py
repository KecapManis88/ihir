from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
import yt_dlp
import os
import uuid
import threading
import time

app = Flask(__name__)
CORS(app, origins=["https://ihir.my.id", "http://localhost"])

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ——— Auto cleanup: hapus file > 10 menit ———
def cleanup_old_files():
    while True:
        now = time.time()
        for fname in os.listdir(DOWNLOAD_DIR):
            fpath = os.path.join(DOWNLOAD_DIR, fname)
            if os.path.isfile(fpath) and now - os.path.getmtime(fpath) > 600:
                os.remove(fpath)
        time.sleep(120)

threading.Thread(target=cleanup_old_files, daemon=True).start()


# ——— GET /info — ambil metadata video ———
@app.route("/info", methods=["GET"])
def get_info():
    url = request.args.get("url", "").strip()
    if not url:
        return jsonify({"error": "URL kosong"}), 400

    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return jsonify({
            "title":     info.get("title", "Unknown"),
            "uploader":  info.get("uploader", "Unknown"),
            "duration":  info.get("duration", 0),
            "thumbnail": info.get("thumbnail", ""),
            "view_count":info.get("view_count", 0),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ——— POST /download — proses dan kirim file ———
@app.route("/download", methods=["POST"])
def download():
    data    = request.get_json()
    url     = (data.get("url") or "").strip()
    fmt     = (data.get("format") or "mp4").lower()
    quality = (data.get("quality") or "best").lower()

    if not url:
        return jsonify({"error": "URL kosong"}), 400

    file_id  = str(uuid.uuid4())
    out_tmpl = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    # Build yt-dlp options
    if fmt == "mp3":
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": out_tmpl,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality.replace("k", "") if "k" in quality else "192",
            }],
            "quiet": True,
        }
        ext = "mp3"

    elif fmt == "m4a":
        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": out_tmpl,
            "quiet": True,
        }
        ext = "m4a"

    elif fmt == "webm":
        res = quality.replace("p","") if "p" in quality else None
        ydl_opts = {
            "format": f"bestvideo[height<={res}][ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best" if res else "best[ext=webm]/best",
            "outtmpl": out_tmpl,
            "quiet": True,
        }
        ext = "webm"

    else:  # mp4 default
        res = quality.replace("p","") if "p" in quality else None
        ydl_opts = {
            "format": f"bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res}]/best" if res else "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
            "outtmpl": out_tmpl,
            "merge_output_format": "mp4",
            "quiet": True,
        }
        ext = "mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "video")

        # Cari file hasil download
        out_file = None
        for fname in os.listdir(DOWNLOAD_DIR):
            if fname.startswith(file_id):
                out_file = os.path.join(DOWNLOAD_DIR, fname)
                ext = fname.rsplit(".", 1)[-1]
                break

        if not out_file or not os.path.exists(out_file):
            return jsonify({"error": "File tidak ditemukan setelah download"}), 500

        # Hapus file setelah dikirim
        @after_this_request
        def remove_file(response):
            try:
                os.remove(out_file)
            except Exception:
                pass
            return response

        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
        download_name = f"{safe_title[:60]}.{ext}"

        return send_file(
            out_file,
            as_attachment=True,
            download_name=download_name,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
