import os, numpy as np
try:
    import torch
except Exception:
    torch = None

class AggressionDetector:
    def __init__(self, model_path="models/fight_model.pt", device="cpu"):
        self.device = device
        self.model = None
        if os.path.exists(model_path) and torch is not None:
            try:
                self.model = torch.load(model_path, map_location=device)
                self.model.eval()
            except Exception as e:
                print('fight model load error:', e)
                self.model = None
        self.track_hist = {}

    def update_positions(self, tracks, maxlen=10):
        for t in tracks:
            tid = t['track_id']
            x1,y1,x2,y2 = t['bbox']
            cx = int((x1+x2)/2); cy = int((y1+y2)/2)
            hist = self.track_hist.get(tid, [])
            hist = hist[-(maxlen-1):] + [(cx,cy)]
            self.track_hist[tid] = hist
        valid = [t['track_id'] for t in tracks]
        for tid in list(self.track_hist.keys()):
            if tid not in valid:
                del self.track_hist[tid]

    def heuristic_detect(self, tracks):
        aggr = set()
        velocities = {}
        for tid, hist in self.track_hist.items():
            if len(hist) >= 2:
                x1,y1 = hist[-2]; x2,y2 = hist[-1]
                velocities[tid] = (x2-x1, y2-y1)
            else:
                velocities[tid] = (0,0)
        for tid, v in velocities.items():
            speed = (v[0]**2 + v[1]**2)**0.5
            if speed > 60:
                aggr.add(tid)
        ids = list(self.track_hist.keys())
        for i in range(len(ids)):
            for j in range(i+1, len(ids)):
                a = self.track_hist[ids[i]][-1]
                b = self.track_hist[ids[j]][-1]
                dist = ((a[0]-b[0])**2 + (a[1]-b[1])**2)**0.5
                if dist < 80:
                    aggr.add(ids[i]); aggr.add(ids[j])
        return aggr

    def detect(self, frame, tracks):
        self.update_positions(tracks)
        if self.model is not None and torch is not None:
            try:
                return self.predict_with_model(frame, tracks)
            except Exception:
                pass
        return self.heuristic_detect(tracks)

    def predict_with_model(self, frame, tracks):
        aggr = set()
        import cv2
        from torchvision import transforms
        tr = transforms.Compose([transforms.ToPILImage(), transforms.Resize((224,224)), transforms.ToTensor()])
        for t in tracks:
            x1,y1,x2,y2 = t['bbox']
            crop = frame[y1:y2, x1:x2]
            if crop.size == 0: continue
            inp = tr(crop).unsqueeze(0).to(self.device)
            out = self.model(inp)
            if isinstance(out, tuple): out = out[0]
            probs = torch.softmax(out, dim=1).cpu().detach().numpy()
            if probs[0,1] > 0.6:
                aggr.add(t['track_id'])
        return aggr
