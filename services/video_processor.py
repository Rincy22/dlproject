import cv2
import os
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolov8n.pt")

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def process_video(filepath, file_id):
    try:
        cap = cv2.VideoCapture(filepath)

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps else 0

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        max_people = 0
        total_people = 0
        unique_ids = set()

        frame_count = 0
        thumbnail_path = os.path.join(BASE_DIR, "reports", f"{file_id}_thumb.jpg")

        # 🔥 FIX: always capture thumbnail once
        thumbnail_saved = False

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # speed optimization
            if frame_count % 2 != 0:
                continue

            # 🔥 FIX: save thumbnail properly
            if not thumbnail_saved:
                cv2.imwrite(thumbnail_path, frame)
                thumbnail_saved = True

            # 🔥 TRACKING (FINAL CONFIG)
            results = model.track(
                frame,
                persist=True,
                tracker="bytetrack.yaml",
                classes=[0],
                conf=0.2,
                iou=0.5,
                verbose=False
            )

            count = 0

            for r in results:
                if r.boxes is None:
                    continue

                ids_in_frame = []

                for box in r.boxes:
                    cls = int(box.cls[0])

                    if model.names[cls] == "person":
                        count += 1

                        # ✅ REAL TRACKING ONLY
                        if hasattr(box, "id") and box.id is not None:
                            person_id = int(box.id.item())
                            unique_ids.add(person_id)
                            ids_in_frame.append(person_id)

                # 🔥 DEBUG (see this in terminal)
                print("IDs:", ids_in_frame)

            total_people = len(unique_ids)
            max_people = max(max_people, count)

        cap.release()

        unique_people = len(unique_ids)

        # 🔥 Improved density calculation
        area = width * height

        if area > 0:
            density_score = (max_people / area) * 100000
        else:
            density_score = 0

# Convert to readable level
        if density_score < 3:
            density = "Low"
        elif density_score < 7:
            density = "Medium"
        else:
            density = "High"

        # ================= PDF =================
        pdf_path = os.path.join(BASE_DIR, "reports", f"{file_id}.pdf")

        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            name="TitleStyle",
            fontSize=20,
            leading=24,
            alignment=1,
            spaceAfter=20
        )

        section_style = ParagraphStyle(
            name="SectionStyle",
            fontSize=14,
            leading=18,
            spaceAfter=10,
            textColor=colors.darkblue
        )

        content = []

        content.append(Paragraph("SmartCrowdTrack - Video Analysis Report", title_style))

        content.append(Paragraph(
            f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            styles["Normal"]
        ))

        content.append(Spacer(1, 20))

        table_data = [
            ["Metric", "Value"],
            ["Duration", f"{round(duration,2)} sec"],
            ["Resolution", f"{width} x {height}"],
            ["Total Detections", str(total_people)],
            ["Unique People", str(unique_people)],
            ["Peak Crowd Size", str(max_people)],
        ]

        table = Table(table_data, colWidths=[200, 200])

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))

        content.append(Paragraph("Analysis Summary", section_style))
        content.append(table)

        content.append(Spacer(1, 20))

        if os.path.exists(thumbnail_path):
            content.append(Paragraph("Frame Snapshot", section_style))
            content.append(Image(thumbnail_path, width=5*inch, height=3*inch))

        content.append(Spacer(1, 20))

        content.append(Paragraph(
            "Generated by SmartCrowdTrack AI System",
            styles["Italic"]
        ))

        doc.build(content)

        # ================= RETURN =================
        return {
            "total_people": max_people,
            "unique_people": min(len(unique_ids), max_people),
            "max_people": total_people,
            "duration": round(duration, 2),
            "resolution": f"{width}x{height}",
            "density": max_people,
            "pdf_url": f"/download-report/{file_id}.pdf"
        }

    except Exception as e:
        return {"error": str(e)}