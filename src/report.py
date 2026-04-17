import pandas as pd
from datetime import datetime

def generate_report(persons, fights):
    data = {
        "Timestamp": [datetime.now()],
        "Total Persons": [persons],
        "Aggressive Incidents": [fights]
    }

    df = pd.DataFrame(data)
    df.to_csv("reports/event_report.csv", index=False)
