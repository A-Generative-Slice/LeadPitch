import argparse
import time
import os
import sys
import threading
from datetime import datetime, timezone, timedelta
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from src.processor import LeadProcessor

import signal
import atexit
from src.git_util import send_github_notification, clear_github_notifications

app = Flask(__name__)

def handle_exit(signum, frame):
    """Sends a notification to GitHub when the process is killed."""
    print(f"\nShutdown signal received ({signum}). Sending notification...", flush=True)
    send_github_notification("OFFLINE")
    sys.exit(0)

# Register exit handlers
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)
# atexit removed — only send notification on unexpected kills, not normal exits

@app.route("/")
def health_check():
    return "LeadPitch is alive and kicking! 🦅", 200

@app.route("/run")
def manual_run():
    # Trigger a run manually via URL for debugging
    csv_path = "clients.csv"
    dry_run = False
    print("Manual run triggered via /run endpoint", flush=True)
    job(csv_path, dry_run)
    return "Outreach process triggered! Check logs for details. 🚀", 200

def run_scheduler(csv_path, dry_run):
    scheduler = BackgroundScheduler()
    
    # Calculate tomorrow at 12 PM IST
    IST = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(IST)
    tomorrow = now + timedelta(days=1)
    start_date = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 12, 0, 0, tzinfo=IST)
    
    # Run every 15 minutes, starting tomorrow at 12 PM
    scheduler.add_job(job, 'interval', minutes=15, start_date=start_date, args=[csv_path, dry_run])
    
    print(f"Scheduler initialized. First action scheduled for tomorrow at {start_date.strftime('%Y-%m-%d %H:%M:%S %Z')}.", flush=True)
    print("Running one email every 15 minutes (targeting 80 emails/day)...", flush=True)
    scheduler.start()

def job(csv_path, dry_run, all_leads=False):
    print(f"Execution started at {time.ctime()}", flush=True)
    try:
        processor = LeadProcessor(csv_path)
        processor.process_leads(dry_run=dry_run, all_leads=all_leads)
    except Exception as e:
        print(f"Error in job: {e}", flush=True)

def main():
    parser = argparse.ArgumentParser(description="LeadPitch: AI Sales Pitch Automation")
    parser.add_argument("--csv", default="clients.csv", help="Path to the clients CSV file")
    parser.add_argument("--dry-run", action="store_true", help="Generate pitches without sending emails")
    parser.add_argument("--schedule", action="store_true", help="Run as a continuous scheduler")
    parser.add_argument("--all", action="store_true", help="Process all unsent leads sequentially")
    
    args = parser.parse_args()

    # Clear old notifications and start fresh
    clear_github_notifications()
    print("LeadPitch is starting up...", flush=True)

    if args.schedule:
        # Start scheduler in a background thread
        scheduler_thread = threading.Thread(target=run_scheduler, args=(args.csv, args.dry_run))
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        # Start Flask server on the main thread
        port = int(os.environ.get("PORT", 10000))
        app.run(host='0.0.0.0', port=port)
    else:
        job(args.csv, args.dry_run, all_leads=args.all)

if __name__ == "__main__":
    main()
