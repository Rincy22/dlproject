import cv2
import numpy as np

heatmap_accumulator = None

def update_heatmap(frame, detections):
    global heatmap_accumulator

    if heatmap_accumulator is None:
        heatmap_accumulator = np.zeros(frame.shape[:2], dtype=np.float32)

    for (x, y, w, h) in detections:
        cx, cy = int(x + w/2), int(y + h/2)
        heatmap_accumulator[cy, cx] += 1

    heatmap = cv2.normalize(heatmap_accumulator, None, 0, 255, cv2.NORM_MINMAX)
    heatmap = heatmap.astype(np.uint8)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    cv2.imwrite("src/static/heatmap.jpg", heatmap)
