import json
import os
import random
import shutil
import threading
import time
import uuid
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request, send_from_directory
from PIL import Image, ImageOps
from werkzeug.utils import secure_filename

from split import compute_piece_boxes, export_pieces, generate_edge_map


BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
UPLOAD_DIR = TEMP_DIR / "uploads"
PUZZLE_DIR = TEMP_DIR / "puzzles"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

with (BASE_DIR / "index.html").open("r", encoding="utf-8") as handle:
  INDEX_HTML = handle.read()


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def ensure_directories() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    PUZZLE_DIR.mkdir(parents=True, exist_ok=True)


def build_puzzle(image_path: Path, output_dir: Path, rows: int, cols: int, tab_size: float) -> dict:
    with Image.open(image_path) as image:
        image = image.convert("RGBA")
        piece_w = image.width // cols
        piece_h = image.height // rows
        if piece_w == 0 or piece_h == 0:
            raise ValueError("图片尺寸太小，无法按指定行列切分。")

        crop_w = piece_w * cols
        crop_h = piece_h * rows
        image = image.crop((0, 0, crop_w, crop_h))
        boxes = compute_piece_boxes(crop_w, crop_h, rows, cols)
        tab_radius = max(2, int(min(piece_w, piece_h) * tab_size / 2))
        padded_image = ImageOps.expand(image, border=tab_radius, fill=(0, 0, 0, 0))
        edge_map = generate_edge_map(rows, cols, random.Random(), border_tabs=False)
        pieces = export_pieces(
            padded_image,
            boxes,
            edge_map,
            piece_w,
            piece_h,
            tab_radius,
            tab_radius,
            rows,
            cols,
            str(output_dir),
            "png",
        )

    puzzle_id = output_dir.name
    metadata = {
        "id": puzzle_id,
        "rows": rows,
        "cols": cols,
        "image_width": crop_w,
        "image_height": crop_h,
        "pieces": [
            {
                **piece.__dict__,
                "url": f"/puzzles/{puzzle_id}/{piece.file}",
            }
            for piece in pieces
        ],
    }
    with (output_dir / "pieces.json").open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, ensure_ascii=False, indent=2)
    return metadata


@app.get("/")
def index():
    return render_template_string(INDEX_HTML)


@app.post("/api/puzzles")
def create_puzzle():
    ensure_directories()
    uploaded = request.files.get("image")
    if uploaded is None or uploaded.filename == "":
        return jsonify({"error": "请先选择一张图片。"}), 400
    if not allowed_file(uploaded.filename):
        return jsonify({"error": "不支持的图片格式，请使用 png/jpg/jpeg/webp/bmp。"}), 400

    try:
        rows = int(request.form.get("rows", 4))
        cols = int(request.form.get("cols", 4))
        tab_size = float(request.form.get("tab_size", 0.35))
    except ValueError:
        return jsonify({"error": "行数、列数和凸起大小必须是数字。"}), 400

    if not (2 <= rows <= 10 and 2 <= cols <= 10):
        return jsonify({"error": "行数和列数必须在 2 到 10 之间。"}), 400
    if not 0.1 <= tab_size <= 0.45:
        return jsonify({"error": "凸起大小必须在 0.1 到 0.45 之间。"}), 400

    puzzle_id = uuid.uuid4().hex
    filename = secure_filename(uploaded.filename)
    suffix = Path(filename).suffix or ".png"
    upload_path = UPLOAD_DIR / f"{puzzle_id}{suffix}"
    output_dir = PUZZLE_DIR / puzzle_id
    output_dir.mkdir(parents=True, exist_ok=True)
    uploaded.save(upload_path)

    try:
        metadata = build_puzzle(upload_path, output_dir, rows, cols, tab_size)
    except Exception as exc:
        shutil.rmtree(output_dir, ignore_errors=True)
        upload_path.unlink(missing_ok=True)
        return jsonify({"error": str(exc)}), 400

    return jsonify(metadata)


@app.get("/puzzles/<puzzle_id>/<path:filename>")
def puzzle_file(puzzle_id: str, filename: str):
    return send_from_directory(PUZZLE_DIR / puzzle_id, filename)


@app.post("/api/shutdown")
def shutdown():
    shutdown_func = request.environ.get("werkzeug.server.shutdown")

    def stop_server() -> None:
        time.sleep(0.3)
        if shutdown_func is not None:
            shutdown_func()
        else:
            os._exit(0)

    threading.Thread(target=stop_server, daemon=True).start()
    return jsonify({"message": "软件已关闭，你可以关闭此页面。"})


def open_browser() -> None:
    webbrowser.open("http://127.0.0.1:5000/")


if __name__ == "__main__":
    ensure_directories()
    threading.Timer(0.8, open_browser).start()
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
