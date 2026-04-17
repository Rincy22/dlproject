import os
import uuid
from flask import Blueprint, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
from services.video_processor import process_video

video_report_bp = Blueprint("video_report", __name__)

UPLOAD_FOLDER = "uploads"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_FOLDER = os.path.join(BASE_DIR, "reports")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)


@video_report_bp.route("/video-upload")
def video_upload_page():
    return render_template("video_upload.html")


@video_report_bp.route("/upload-video-report", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["video"]

    if file.filename == "":
        return jsonify({"error": "Empty file"}), 400

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4()}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_name)

    file.save(filepath)

    # ✅ DIRECT PROCESS (NO THREAD)
    result = process_video(filepath, unique_name)

    return jsonify(result)


@video_report_bp.route("/download-report/<filename>")
def download_report(filename):
    path = os.path.join(REPORT_FOLDER, filename)

    if not os.path.exists(path):
        return jsonify({"error": "Report not found"}), 404

    return send_file(path, as_attachment=True)