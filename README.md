# AggressionDetectionSystem (SmartCrowdTrack)

This ZIP contains a runnable demo project for SmartCrowdTrack — a real-time crowd monitoring and aggression detection prototype.
Open in VS Code and follow the README instructions below.

## Quick start
1. Create and activate a Python venv (Python 3.8+):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Place real model files in `models/` if you have them (optional):
   - models/yolov8n.pt
   - models/fight_model.pt
   The archive contains small placeholder files; replace with proper models for best results.
4. Run demo server:
   ```
   python src/app.py
   ```
5. Open browser at http://127.0.0.1:5000
