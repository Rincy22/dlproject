import cv2
import numpy as np
import time
from ultralytics import YOLO
from threading import Lock
from deep_sort_realtime.deepsort_tracker import DeepSort
from datetime import datetime

# ================= REPORT STORAGE =================
REPORT_DATA = {
    "unique_people": 0,
    "aggression": 0,
    "peak_density": 0,
    "incident_log": []
}

# ================= LOAD MODELS =================
model = YOLO("yolov8s.pt")

tracker = DeepSort(
    max_age=40,
    n_init=3,
    max_iou_distance=0.7
)

cap = cv2.VideoCapture(0)

# ================= GLOBAL STATE =================
unique_ids = set()
confirmed_ids = set()
track_birth_time = {}

aggression_count = 0
heatmap = None
peak_density = 0
heatmap_lock = Lock()

# ================= ZONE COUNTS =================
zone_counts = {"A": 0, "B": 0}

# ================= STABILIZATION =================
STABLE_TIME = 2.0

# ================= AGGRESSION PARAMETERS =================
DISTANCE_THRESHOLD = 80
GROUP_TIME_THRESHOLD = 4
COOLDOWN_TIME = 8

pair_start_times = {}
pair_cooldown = {}

# ================= MAIN VIDEO STREAM =================
def generate_frames():
    global aggression_count, heatmap, peak_density, zone_counts

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]

        # 🔥 ZONE POLYGONS (HIDDEN LOGIC ONLY)
        ZONE_A_POLY = np.array([
            [int(0.05*w), int(0.1*h)],
            [int(0.45*w), int(0.1*h)],
            [int(0.45*w), int(0.8*h)],
            [int(0.05*w), int(0.8*h)]
        ])

        ZONE_B_POLY = np.array([
            [int(0.55*w), int(0.1*h)],
            [int(0.95*w), int(0.1*h)],
            [int(0.95*w), int(0.8*h)],
            [int(0.55*w), int(0.8*h)]
        ])

        if heatmap is None:
            heatmap = np.zeros((h, w), dtype=np.float32)

        results = model(frame, conf=0.55, classes=[0])
        detections = []
        frame_area = h * w

        # Reset zone counts
        zone_counts["A"] = 0
        zone_counts["B"] = 0

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()

                if (x2 - x1) * (y2 - y1) > 0.35 * frame_area:
                    continue

                detections.append(([x1, y1, x2 - x1, y2 - y1], conf, "person"))

        tracks = tracker.update_tracks(detections, frame=frame)
        current_time = time.time()
        centers = {}

        for track in tracks:
            if not track.is_confirmed():
                continue

            track_id = track.track_id

            if track_id not in track_birth_time:
                track_birth_time[track_id] = current_time

            if current_time - track_birth_time[track_id] >= STABLE_TIME:
                confirmed_ids.add(track_id)
                unique_ids.add(track_id)

            if track_id not in confirmed_ids:
                continue

            l, t, r, b = map(int, track.to_ltrb())
            cx, cy = int((l + r) / 2), int((t + b) / 2)
            centers[track_id] = (cx, cy)

            # ================= ZONE DETECTION =================
            if cv2.pointPolygonTest(ZONE_A_POLY, (cx, cy), False) >= 0:
                zone_counts["A"] += 1
            elif cv2.pointPolygonTest(ZONE_B_POLY, (cx, cy), False) >= 0:
                zone_counts["B"] += 1

            # ================= HEATMAP =================
            with heatmap_lock:
                if 0 <= cx < heatmap.shape[1] and 0 <= cy < heatmap.shape[0]:
                    heatmap[cy, cx] += 1
                    peak_density = max(peak_density, heatmap[cy, cx])

            # ================= DRAW PERSON ONLY =================
            cv2.rectangle(frame, (l, t), (r, b), (0, 255, 0), 2)
            cv2.putText(frame, f"Person {track_id}", (l, t - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # ❌ REMOVED ZONE TEXT DRAWING → CLEAN UI

        # ================= AGGRESSION =================
        ids = list(centers.keys())
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                id1, id2 = ids[i], ids[j]
                p1, p2 = centers[id1], centers[id2]

                dist = np.hypot(p1[0] - p2[0], p1[1] - p2[1])
                pair = tuple(sorted((id1, id2)))

                if dist < DISTANCE_THRESHOLD:
                    if pair not in pair_start_times:
                        pair_start_times[pair] = current_time

                    elapsed = current_time - pair_start_times[pair]
                    last_count = pair_cooldown.get(pair, 0)

                    if elapsed >= GROUP_TIME_THRESHOLD and current_time - last_count > COOLDOWN_TIME:
                        aggression_count += 1
                        pair_cooldown[pair] = current_time
                        log_incident()
                else:
                    pair_start_times.pop(pair, None)

        _, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

# ================= INCIDENT LOGGER =================
def log_incident():
    REPORT_DATA["incident_log"].append({
        "time": datetime.now().strftime("%H:%M"),
        "count": aggression_count
    })

# ================= HEATMAP =================
def get_heatmap_frame():
    with heatmap_lock:
        if heatmap is None:
            return None

        heatmap_blur = cv2.GaussianBlur(heatmap, (31, 31), 0)
        heatmap_norm = cv2.normalize(heatmap_blur, None, 0, 255, cv2.NORM_MINMAX)
        heatmap_color = cv2.applyColorMap(
            heatmap_norm.astype(np.uint8),
            cv2.COLORMAP_JET
        )

        _, buffer = cv2.imencode(".jpg", heatmap_color)
        return buffer.tobytes()

# ================= STATS =================
def get_stats():
    person_count = len(unique_ids)
    density_percent = min(100, int((person_count / 6) * 100))

    REPORT_DATA["unique_people"] = person_count
    REPORT_DATA["aggression"] = aggression_count
    REPORT_DATA["peak_density"] = max(REPORT_DATA["peak_density"], density_percent)

    return {
        "total_people": person_count,
        "aggression_count": aggression_count,
        "peak_density": density_percent,
        "incidents_over_time": [
            i["count"] for i in REPORT_DATA["incident_log"][-6:]
        ]
    }

# ================= LOCATION =================
def get_location_stats():
    stats = get_stats()

    return {
        "total_zones": 2,
        "total_attendees": stats["total_people"],
        "active_cameras": 1,
        "avg_capacity": stats["peak_density"],
        "zones": [
            {
                "name": "Zone A",
                "people": zone_counts["A"],
                "capacity": 100,
                "status": get_zone_status(zone_counts["A"], 100)
            },
            {
                "name": "Zone B",
                "people": zone_counts["B"],
                "capacity": 100,
                "status": get_zone_status(zone_counts["B"], 100)
            }
        ]
    }

def get_zone_status(count, capacity):
    ratio = count / capacity
    if ratio < 0.5:
        return "Normal"
    elif ratio < 0.8:
        return "Warning"
    else:
        return "Critical"

# ================= REPORT =================
def generate_report():
    return f"""
SmartCrowdTrack Report
----------------------
Unique Persons Detected : {len(unique_ids)}
Aggressive Incidents   : {aggression_count}
Peak Crowd Density     : {peak_density}%
"""