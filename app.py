import os, subprocess, uuid, json, sqlite3
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
import static_ffmpeg  # এটি নিশ্চিত কর

# FFmpeg সেটআপ
static_ffmpeg.add_paths()

app = Flask(__name__)
app.secret_key = "projectx_secret_key_2026"

# ================= DIRECTORY SETUP =================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "cloud_files")

USER_DB = os.path.join(BASE_DIR, "users_data.db")
ADMIN_DB = os.path.join(BASE_DIR, "admin_panel.db")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HISTORY_FILE = os.path.join(BASE_DIR, "history.json")

# ================= HELPERS =================
def save_to_history(data):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except:
            history = []
    history.insert(0, data)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

def get_db(db_type="user"):
    db_path = USER_DB if db_type == "user" else ADMIN_DB
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_domain(url: str) -> str:
    return urlparse(url).netloc.lower()

# ================= ROUTES =================
@app.route("/")
def index():
    return render_template("index.html")

# ---------- AUTH ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")

        db = get_db("user")
        res = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (user, pwd)
        ).fetchone()
        db.close()

        if res:
            session["user_name"] = user
            return redirect(url_for("index"))
        return render_template("login.html", error="Wrong credentials ❌")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")

        try:
            db = get_db("user")
            db.execute("INSERT INTO users (username,password) VALUES (?,?)", (user, pwd))
            db.commit()
            db.close()
            session["user_name"] = user
            return redirect(url_for("index"))
        except sqlite3.IntegrityError:
            return "User already exists ❌"
    return render_template("signup.html")

@app.route("/guest-mode")
def guest_mode():
    session["user_name"] = "Guest"
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.pop("user_name", None)
    session.pop("admin_logged_in", None)
    return redirect(url_for("index"))

# ---------- PREVIEW ----------
@app.route("/preview", methods=["POST"])
def preview():
    url = request.json.get("url")
    if not url:
        return jsonify({"success": False, "message": "No URL provided"})

    print(f"Processing URL: {url}")

    try:
        cmd = [
            "yt-dlp",
            "-J",
            "--no-playlist",
            "--force-ipv4",
            "--user-agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            url
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"❌ Preview Error: {result.stderr}")
            return jsonify({
                "success": False,
                "message": "Preview failed for this URL."
            })

        info = json.loads(result.stdout)

        return jsonify({
            "success": True,
            "thumbnail": info.get("thumbnail"),
            "title": info.get("title", "Unknown Video"),
            "meta": f"Site: {info.get('extractor_key', 'Unknown')} | Length: {info.get('duration', 0)}s"
        })

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return jsonify({"success": False, "message": "Internal error while previewing."})

# ---------- DOWNLOAD ----------
@app.route("/download", methods=["POST"])
def download():
    data = request.json
    url = data.get("url")
    ftype = data.get("format", "mp4")

    if not url:
        return jsonify({"success": False, "message": "No URL provided"})

    file_id = str(uuid.uuid4())

    common_flags = [
        "--force-ipv4",
        "--user-agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    ]

    # ---------- MP3 ----------
    if ftype == "mp3":
        cmd = [
            "yt-dlp",
            *common_flags,
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", os.path.join(DOWNLOAD_DIR, f"{file_id}.mp3"),
            url,
        ]

    # ---------- VIDEO (MP4) ----------
    else:
        # ONE universal format for all platforms
        fmt = "bestvideo+bestaudio/best"  # universal best video+audio / fallback best [web:93][web:66]

        cmd = [
            "yt-dlp",
            *common_flags,
            "--no-playlist",
            "-f", fmt,
            "-o", os.path.join(DOWNLOAD_DIR, f"{file_id}.mp4"),
            url,
        ]

    print("CMD:", " ".join(cmd))
    print(f"⬇️ Downloading: {url}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(file_id):
                save_to_history({"filename": f, "url": url})
                return jsonify({"success": True, "filename": f})

    print(f"❌ Download Failed: {result.stderr}")
    return jsonify({"success": False, "message": result.stderr})

# ---------- FILE ----------
@app.route("/file/<filename>")
def file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

# ---------- DASHBOARD ----------
@app.route("/dashboard")
@app.route("/dash-board")
def dashboard():
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
    return render_template("dashboard.html", history=history)

@app.route("/download-contents")
@app.route("/downloadcontents")
def contents():
    return render_template("contents.html")

@app.route("/manage-password")
@app.route("/passwords")
def passwords():
    return render_template("passwords.html")

@app.route("/settings-for-users")
@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/cloud-storage")
@app.route("/cloud")
def cloud_storage():
    return render_template("cloud.html")

# ---------- CLOUD UPLOAD ----------
@app.route("/upload-cloud", methods=["POST"])
def upload_cloud():
    file = request.files.get("file")
    if not file:
        return jsonify({"success": False})
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return jsonify({"success": True})

# ---------- ADMIN ----------
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")

        db = get_db("admin")
        admin = db.execute(
            "SELECT * FROM admins WHERE admin_name=? AND admin_pass=?",
            (user, pwd)
        ).fetchone()
        db.close()

        if admin:
            session["admin_logged_in"] = True
            return redirect(url_for("dashboard"))
        return "Invalid admin ❌"
    return render_template("login.html")

# ---------- PASSWORD VAULT ----------
@app.route("/save-password", methods=["POST"])
def save_password():
    if "user_name" not in session:
        return jsonify({"success": False})

    data = request.json
    db = get_db("user")
    user = db.execute(
        "SELECT id FROM users WHERE username=?",
        (session["user_name"],)
    ).fetchone()

    if user:
        db.execute(
            "INSERT INTO password_vault (user_id, site_name, site_url, encrypted_password) VALUES (?,?,?,?)",
            (user["id"], data["site"], data["url"], data["password"])
        )
        db.commit()
        db.close()
        return jsonify({"success": True})
    return jsonify({"success": False})

# ================= RUN =================
def init_db():
    with sqlite3.connect(USER_DB) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            joined_date DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS password_vault(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            site_name TEXT,
            site_url TEXT,
            encrypted_password TEXT
        )""")
        conn.commit()

    with sqlite3.connect(ADMIN_DB) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS admins(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_name TEXT UNIQUE,
            admin_pass TEXT
        )""")
        conn.execute(
            "INSERT OR IGNORE INTO admins (admin_name,admin_pass) VALUES (?,?)",
            ("admin", "123")
        )
        conn.commit()

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
