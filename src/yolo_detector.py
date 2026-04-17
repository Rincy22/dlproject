from ultralytics import YOLO
import cv2, numpy as np
class YOLODetector:
    def __init__(self, model_path="models/yolov8n.pt", device=None):
        try:
            self.model = YOLO(model_path)
            if device:
                self.model.to(device)
        except Exception as e:
            print('YOLO model load error:', e)
            self.model = None
    def detect(self, frame):
        if self.model is None:
            return []
        results = self.model.predict(source=frame, conf=0.4, imgsz=640, verbose=False)
        res = results[0]
        dets = []
        if hasattr(res, 'boxes') and res.boxes is not None and len(res.boxes) > 0:
            boxes = res.boxes.xyxy.cpu().numpy()
            confs = res.boxes.conf.cpu().numpy()
            cls = res.boxes.cls.cpu().numpy().astype(int)
            for (b,cg,cl) in zip(boxes, confs, cls):
                x1,y1,x2,y2 = b
                dets.append([int(x1), int(y1), int(x2), int(y2), float(cg), int(cl)])
        return dets
    def annotate(self, frame, tracks, heatmap=None):
        out = frame.copy()
        for t in tracks:
            x1,y1,x2,y2 = t['bbox']
            tid = t['track_id']
            ag = t.get('aggressive', False)
            color = (0,0,255) if ag else (0,255,0)
            cv2.rectangle(out, (x1,y1), (x2,y2), color, 2)
            cv2.putText(out, f"ID:{tid}", (x1, max(y1-6,0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        if heatmap is not None:
            hm = cv2.resize(heatmap, (out.shape[1], out.shape[0]))
            overlay = cv2.addWeighted(out, 0.7, hm, 0.3, 0)
            return overlay
        return out
