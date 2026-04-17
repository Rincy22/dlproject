import time, os
def ensure_dirs():
    for p in ["output/logs", "output/reports", "data/raw", "data/processed", "models"]:
        os.makedirs(p, exist_ok=True)
def now_str():
    return time.strftime("%Y%m%d_%H%M%S")
