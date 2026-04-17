import sys
import os

# ✅ FIX: Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import io
from datetime import datetime

from flask import Flask, render_template, Response, jsonify, send_file, request
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from vision import get_location_stats

# Alias
from vision import (
    generate_frames,
    get_stats,
    generate_report as build_text_report,
    get_heatmap_frame,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

# ✅ KEEP YOUR BLUEPRINT
from routes.video_report import video_report_bp
app.register_blueprint(video_report_bp)

# ================= SETTINGS DATA =================
SETTINGS_DATA = {
    "name": "Admin User",
    "email": "admin@gmail.com",
    "phone": "+91 9876543210",
    "department": "Security",
    "email_alerts": True,
    "sms_alerts": False,
    "push_notifications": True
}

# ================= DASHBOARD =================
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# ================= LOCATION =================
@app.route("/location")
@app.route("/locations")
def location():
    return render_template("location.html")

# ================= SETTINGS =================
@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/get-settings")
def get_settings():
    return jsonify(SETTINGS_DATA)

@app.route("/save-settings", methods=["POST"])
def save_settings():
    data = request.json
    SETTINGS_DATA.update(data)
    return jsonify({"status": "success"})

# ================= REPORT PAGE =================
@app.route("/report")
def report():
    return render_template("report.html")

# ================= VIDEO =================
@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )

# ================= STATS =================
@app.route("/stats")
def stats():
    return jsonify(get_stats())

# ================= REPORT DATA (FIXED CHART) =================
@app.route("/report-data")
def report_data():
    stats = get_stats()

    incidents = stats.get("incidents_over_time", [])

    # ✅ FIX: Always show chart
    if not incidents:
        incidents = [0, 0, 0, 0, 0]

    return jsonify({
        "total_unique_people": stats.get("total_people", 0),
        "aggression_incidents": stats.get("aggression_count", 0),
        "peak_crowd_density": stats.get("peak_density", 0),
        "incidents_over_time": incidents
    })

# ================= TXT REPORT =================
@app.route("/download-report")
def download_report():
    report_text = build_text_report()

    buffer = io.BytesIO()
    buffer.write(report_text.encode("utf-8"))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="monitoring_report.txt",
        mimetype="text/plain",
    )

# ================= PDF REPORT (IMPROVED) =================
@app.route("/generate-report")
def generate_pdf_report():
    stats = get_stats()

    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    content = []

    # Title
    content.append(Paragraph(
        "SmartCrowdTrack – Crowd Analytics Report",
        ParagraphStyle(
            'title',
            fontSize=20,
            textColor=colors.HexColor("#1e3a8a"),
            spaceAfter=10
        )
    ))

    content.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
        styles["Normal"]
    ))

    content.append(Spacer(1, 15))

    content.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563eb")))
    content.append(Spacer(1, 20))

    content.append(Paragraph(
        "Summary Metrics",
        ParagraphStyle(
            'section',
            fontSize=14,
            textColor=colors.HexColor("#2563eb"),
            spaceAfter=10
        )
    ))

    table_data = [
        ["Total People", str(stats.get("total_people", 0))],
        ["Aggression Incidents", str(stats.get("aggression_count", 0))],
        ["Peak Density", f"{stats.get('peak_density', 0)} %"],
    ]

    table = Table(table_data, colWidths=[250, 150])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor("#2563eb")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))

    content.append(table)
    content.append(Spacer(1, 40))

    content.append(Paragraph(
        "SmartCrowdTrack • AI Crowd Monitoring System",
        ParagraphStyle(
            'footer',
            alignment=1,
            textColor=colors.HexColor("#64748b"),
            fontSize=9
        )
    ))

    pdf.build(content)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="SmartCrowd_Report.pdf",
        mimetype="application/pdf",
    )

# ================= HEATMAP =================
@app.route("/heatmap_feed")
def heatmap_feed():
    frame = get_heatmap_frame()
    if frame is None:
        return "", 204

    return Response(frame, mimetype="image/jpeg")

# ================= LOCATION DATA =================
@app.route("/location-data")
def location_data():
    return jsonify(get_location_stats())

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True, threaded=True)