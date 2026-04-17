import cv2, time, os
from yolo_detector import YOLODetector
from tracker import Tracker
from aggression import AggressionDetector
from heatmap import Heatmap
from report import save_report
from utils import ensure_dirs, now_str
ensure_dirs()
def run(source=0):
    cap = cv2.VideoCapture(source)
    ret, frame = cap.read()
    if not ret:
        print('Cannot open source'); return
    detector = YOLODetector()
    tracker = Tracker()
    ag = AggressionDetector()
    heat = Heatmap(frame.shape)
    unique_ids = set(); log = []
    while True:
        ret, frame = cap.read()
        if not ret: break
        dets = detector.detect(frame)
        tracks = tracker.update(dets, frame)
        for t in tracks: unique_ids.add(t['track_id'])
        aggr_ids = ag.detect(frame, tracks)
        for t in tracks: t['aggressive'] = t['track_id'] in aggr_ids
        centroids = [((t['bbox'][0]+t['bbox'][2])//2, (t['bbox'][1]+t['bbox'][3])//2) for t in tracks]
        heat.add_points(centroids)
        annotated = detector.annotate(frame, tracks, heatmap=heat.render())
        state = {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'total_unique': len(unique_ids), 'current_count': len(tracks), 'aggression_count': len(aggr_ids)}
        log.append(state)
        cv2.imshow('SmartCrowdTrack', annotated)
        if cv2.waitKey(1)&0xFF==ord('q'): break
    cap.release(); cv2.destroyAllWindows()
    os.makedirs('output/reports', exist_ok=True); fname, chart = save_report(log)
    print('Saved report:', fname, chart)
if __name__=='__main__':
    run(0)
