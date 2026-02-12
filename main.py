import argparse
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from src.processor import LeadProcessor

def job(csv_path, dry_run):
    print(f"Execution started at {time.ctime()}")
    processor = LeadProcessor(csv_path)
    processor.process_leads(dry_run=dry_run)

def main():
    parser = argparse.ArgumentParser(description="LeadPitch: AI Sales Pitch Automation")
    parser.add_argument("--csv", default="clients.csv", help="Path to the clients CSV file")
    parser.add_argument("--dry-run", action="store_true", help="Generate pitches without sending emails")
    parser.add_argument("--schedule", action="store_true", help="Run as a continuous scheduler")
    
    args = parser.parse_args()

    if args.schedule:
        scheduler = BlockingScheduler()
        # Run every 10 minutes
        scheduler.add_job(job, 'interval', minutes=10, args=[args.csv, args.dry_run], next_run_time=None)
        print("Scheduler started. Running one email every 10 minutes...")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass
    else:
        job(args.csv, args.dry_run)

if __name__ == "__main__":
    main()
