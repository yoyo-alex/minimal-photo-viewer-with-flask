from flask import Flask, render_template, send_from_directory
import os
from datetime import datetime

app = Flask(__name__)

# 照片文件夹
PHOTO_DIR = "photos"

# 支持的图片扩展名
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".gif"}


def get_photos_by_date():
    """按日期分组照片"""
    photos = {}
    for fname in os.listdir(PHOTO_DIR):
        fpath = os.path.join(PHOTO_DIR, fname)
        ext = os.path.splitext(fname)[1].lower()
        if os.path.isfile(fpath) and ext in ALLOWED_EXT:
            # 获取文件修改时间作为日期
            date = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%d")
            photos.setdefault(date, []).append(fname)

    # 按日期倒序排列
    return dict(sorted(photos.items(), reverse=True))


@app.route("/")
def gallery():
    photos = get_photos_by_date()
    return render_template("gallery.html", photos=photos)


@app.route("/photos/<path:filename>")
def serve_photo(filename):
    return send_from_directory(PHOTO_DIR, filename)


if __name__ == "__main__":
    os.makedirs(PHOTO_DIR, exist_ok=True)
    app.run(debug=True)
