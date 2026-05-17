# scheduler.py
# Runs the content agent on a default transcript every day at 9am Doha time.
# Doha is UTC+3.
# Run with: python scheduler.py
# Keep this terminal window open — it checks the time every minute.

import schedule
# schedule is a lightweight Python library for running functions at set times.
# Install it: pip install schedule (add to requirements.txt after)

import time
import json
from datetime import datetime
from zoneinfo import ZoneInfo
# zoneinfo is a built-in Python library (3.9+) for timezone handling.
# ZoneInfo("Asia/Qatar") gives us Doha's timezone automatically,
# including any future changes — more reliable than manually adding 3 hours.

from agent import run_agent

DOHA_TZ = ZoneInfo("Asia/Qatar")

def scheduled_job():
    """
    The function that runs every day at 9am Doha time.
    In production: would fetch the latest transcript from Granola API.
    In this demo: reads from sample_input.txt as a stand-in.
    """
    
    now = datetime.now(DOHA_TZ)
    print(f"[{now.strftime('%Y-%m-%d %H:%M')} Doha] Running scheduled content agent...")
    
    # Read the default transcript
    # In a real deployment, this would call the Granola API
    # to fetch the most recent transcript automatically.
    try:
        with open("sample_input.txt", "r", encoding="utf-8") as f:
            transcript = f.read()
    except FileNotFoundError:
        print("No sample_input.txt found. Skipping run.")
        return
    
    result = run_agent(transcript)
    
    # Save with timestamp
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    filename = f"scheduled_output_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Scheduled run complete. Output saved to {filename}")

# Schedule the job for 09:00 every day.
# schedule uses the LOCAL system time by default.
# We adjust: if your machine is not in Doha time,
# set your system timezone or use the UTC equivalent.
# UTC equivalent of 9am Doha (UTC+3) = 06:00 UTC.

schedule.every().day.at("06:00").do(scheduled_job)
# .every().day.at("HH:MM") — self explanatory.
# .do(scheduled_job) — run this function at that time.

print("Scheduler running. Will execute daily at 09:00 Doha time (06:00 UTC).")
print("Press Ctrl+C to stop.")

# This loop keeps the script alive, checking every 60 seconds
# whether it's time to run the job.
while True:
    schedule.run_pending()
    # run_pending() checks: is there a job scheduled for right now?
    # If yes, run it. If no, do nothing.
    time.sleep(60)
    # Sleep for 60 seconds before checking again.
    # This prevents the loop from consuming 100% CPU.