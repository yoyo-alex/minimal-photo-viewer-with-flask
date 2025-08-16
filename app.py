from flask import Flask, render_template, request, jsonify, send_from_directory
import os, json
from datetime import datetime

app = Flask(__name__)

PHOTO_DIR = "photos"
COMMENT_FILE = "comments.json"
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".gif"}


def load_comments():
    if os.path.exists(COMMENT_FILE):
        with open(COMMENT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_comments(data):
    with open(COMMENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_photos_by_date():
    """
    Returns {'YYYY-MM-DD': ['file1.jpg', ...], ...} sorted by date desc.
    """
    if not os.path.exists(PHOTO_DIR):
        return {}
    photos = {}
    for fname in os.listdir(PHOTO_DIR):
        fpath = os.path.join(PHOTO_DIR, fname)
        ext = os.path.splitext(fname)[1].lower()
        if os.path.isfile(fpath) and ext in ALLOWED_EXT:
            d = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%d")
            photos.setdefault(d, []).append(fname)
    # newest first
    return dict(sorted(photos.items(), reverse=True))


def build_units(photos_by_date):
    """
    -> {date: {"files":[...], "week": int}, ...}
    """
    units = {}
    for date_str, files in photos_by_date.items():
        week_num = datetime.strptime(date_str, "%Y-%m-%d").isocalendar()[1]
        units[date_str] = {"files": files, "week": week_num}
    return units


@app.route("/")
def gallery():
    photos_by_date = get_photos_by_date()
    photos = build_units(photos_by_date)
    comments = load_comments()
    return render_template("gallery.html", photos=photos, comments=comments, title="All Photos")


@app.route("/month/<month>")
def month_view(month):
    """month like 'YYYY-MM'"""
    photos_by_date = get_photos_by_date()
    filtered = {d: fl for d, fl in photos_by_date.items() if d.startswith(month)}
    photos = build_units(filtered)
    comments = load_comments()
    return render_template("gallery.html", photos=photos, comments=comments, title=f"Photos of {month}")


@app.route("/photos/<path:filename>")
def serve_photo(filename):
    return send_from_directory(PHOTO_DIR, filename)


@app.route("/comment", methods=["POST"])
def add_or_update_comment():
    data = request.json or {}
    date = data.get("date", "")
    text = data.get("text", "")

    if not date:
        return jsonify(success=False, error="missing date"), 400

    comments = load_comments()
    comments[date] = text  # one editable comment per date
    save_comments(comments)
    return jsonify(success=True)


if __name__ == "__main__":
    os.makedirs(PHOTO_DIR, exist_ok=True)
    app.run(debug=True)
