from deep_sort_realtime.deepsort_tracker import DeepSort
class Tracker:
    def __init__(self, max_age=30, n_init=3):
        self.tracker = DeepSort(max_age=max_age, n_init=n_init)
    def update(self, detections, frame):
        boxes = []
        confidences = []
        for d in detections:
            x1,y1,x2,y2,c,cl = d
            boxes.append([x1,y1,x2-x1,y2-y1])
            confidences.append(c)
        tracks = self.tracker.update_tracks(boxes, confidences, frame=frame)
        out = []
        for tr in tracks:
            if not tr.is_confirmed():
                continue
            tid = tr.track_id
            l,t,w,h = tr.to_ltwh()
            out.append({"track_id": int(tid), "bbox": [int(l), int(t), int(l+w), int(t+h)]})
        return out
