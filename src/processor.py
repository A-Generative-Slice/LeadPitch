import os
import pandas as pd
from datetime import datetime, timezone, timedelta
from src.agent import PitchAgent
from src.mailer import Mailer
from src.git_util import sync_csv_to_github

DAILY_EMAIL_CAP = int(os.getenv("DAILY_EMAIL_CAP", "100"))
class LeadProcessor:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.agent = PitchAgent()
        self.mailer = Mailer()

    def _emails_sent_today(self, df):
        """Count how many emails were already sent today (IST)."""
        IST = timezone(timedelta(hours=5, minutes=30))
        today_str = datetime.now(IST).strftime('%Y-%m-%d')
        sent_today = 0
        for val in df['Sent Time']:
            if isinstance(val, str) and val.startswith(today_str):
                sent_today += 1
        return sent_today

    def process_leads(self, dry_run=False, all_leads=False):
        """
        Reads CSV, generates pitches, and sends emails for unsent leads.
        If all_leads is True, it loops through everything. If False, it processes only one.
        """
        import time
        try:
            df = pd.read_csv(self.csv_path)
        except Exception as e:
            print(f"Error reading CSV: {e}", flush=True)
            return

        if 'Sent Status' not in df.columns:
            df['Sent Status'] = 'No'
        df['Sent Status'] = df['Sent Status'].fillna('No')

        if 'Sent Time' not in df.columns:
            df['Sent Time'] = ''
        else:
            df['Sent Time'] = df['Sent Time'].astype(object).fillna('')

        # --- Daily cap check ---
        sent_today = self._emails_sent_today(df)
        remaining_today = DAILY_EMAIL_CAP - sent_today
        print(f"📊 Daily cap: {sent_today}/{DAILY_EMAIL_CAP} emails sent today.", flush=True)

        if remaining_today <= 0:
            print(f"🛑 Daily cap of {DAILY_EMAIL_CAP} reached. Resuming automatically tomorrow.", flush=True)
            return

        unsent_leads = df[df['Sent Status'].isin(['No', 'Pitch Failed'])]
        
        print(f"DEBUG: Found {len(df)} total rows in CSV.", flush=True)
        print(f"DEBUG: Found {len(unsent_leads)} leads pending (No + Pitch Failed retries).", flush=True)
        
        if not unsent_leads.empty:
            print(f"DEBUG: First lead in queue: {unsent_leads.iloc[0].get('Client Name')} ({unsent_leads.iloc[0].get('Email ID')})", flush=True)
            self._reset_database_exhausted_flag()

        if unsent_leads.empty:
            print("No new leads to process. Check if 'Sent Status' column is correctly set to 'No' in your CSV.", flush=True)
            self._handle_database_exhausted()
            return

        batch_size = min(int(os.getenv("BATCH_SIZE", "15")), remaining_today)
        leads_to_process = unsent_leads.iloc[:batch_size] if all_leads else unsent_leads.iloc[:1]
        
        for index, row in leads_to_process.iterrows():
            client_name = row.get('Client Name', 'Valued Partner')
            client_email = row.get('Email ID')

            if not client_email or str(client_email).strip() == '' or str(client_email).strip().lower() == 'nan':
                print(f"Skipping lead at index {index}: No email provided for {client_name}", flush=True)
                df.at[index, 'Sent Status'] = 'Invalid Email'
                df.to_csv(self.csv_path, index=False)
                continue

            print(f"Generating pitch for {client_name}...", flush=True)
            subject, body = self.agent.generate_pitch(row.to_dict())

            if not subject or not body:
                print(f"Failed to generate pitch for {client_name}. Marking as failed.", flush=True)
                df.at[index, 'Sent Status'] = 'Pitch Failed'
                df.to_csv(self.csv_path, index=False)
                continue

            if dry_run:
                print(f"--- DRY RUN: Pitch for {client_name} ---", flush=True)
                df.at[index, 'Sent Status'] = 'Dry Run Verified'
            else:
                success, fatal = self.mailer.send_email(client_email, subject, body)
                if success:
                    IST = timezone(timedelta(hours=5, minutes=30))
                    df.at[index, 'Sent Status'] = 'Yes'
                    df.at[index, 'Sent Time'] = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
                elif fatal:
                    print("🛑 FATAL: Gmail daily limit reached. Stopping all sends for today.", flush=True)
                    df.to_csv(self.csv_path, index=False)
                    sync_csv_to_github(self.csv_path)
                    return

            # Save progress locally
            df.to_csv(self.csv_path, index=False)
            print(f"Successfully processed {client_name}.", flush=True)
            
            # Sync back to GitHub if not a dry run
            if not dry_run:
                sync_csv_to_github(self.csv_path)

            if all_leads and index != leads_to_process.index[-1]:
                delay = 120 # 2-min gap between emails (batch mode in Actions)
                print(f"Waiting {delay} seconds for next lead to avoid spam flags...", flush=True)
                time.sleep(delay)

    def _handle_database_exhausted(self):
        """Sends a notification email when there are no more unsent leads in the CSV."""
        import json
        from src.git_util import get_file_from_github, sync_csv_to_github
        
        status_file = "db_status.json"
        already_sent = False
        
        # Try local first
        if os.path.exists(status_file):
            try:
                with open(status_file, "r") as f:
                    data = json.load(f)
                    already_sent = data.get("exhausted_notification_sent", False)
            except:
                pass
        
        # If not local, try fetching from GitHub
        if not already_sent:
            github_content = get_file_from_github(status_file)
            if github_content:
                try:
                    data = json.loads(github_content)
                    already_sent = data.get("exhausted_notification_sent", False)
                except:
                    pass

        if already_sent:
            print("CSV Over notification already sent previously. Skipping to avoid spam.", flush=True)
            return

        # Send notification email
        to_email = "s.m.d.hussainjoe@gmail.com"
        subject = "LeadPitch Alert: Lead Database Exhausted"
        body = """Hi Mohammad,

All leads in clients.csv have been successfully processed. 
The outreach automation is now paused until you add new leads to your CSV database.

Best regards,
LeadPitch Autopilot
"""
        print(f"Database exhausted. Sending notification email to {to_email}...", flush=True)
        success, fatal = self.mailer.send_email(to_email, subject, body)
        if success:
            # Write status file locally
            status_data = {"exhausted_notification_sent": True}
            try:
                with open(status_file, "w") as f:
                    json.dump(status_data, f)
                # Sync status file to GitHub so it persists across Action runs
                sync_csv_to_github(status_file)
                print("Logged and synced database exhausted status to GitHub.", flush=True)
            except Exception as e:
                print(f"Error saving database status: {e}", flush=True)

    def _reset_database_exhausted_flag(self):
        """Resets the exhausted notification flag when new leads are added."""
        import json
        from src.git_util import get_file_from_github, sync_csv_to_github
        
        status_file = "db_status.json"
        already_sent = False
        
        if os.path.exists(status_file):
            try:
                with open(status_file, "r") as f:
                    data = json.load(f)
                    already_sent = data.get("exhausted_notification_sent", False)
            except:
                pass
        
        if not already_sent:
            github_content = get_file_from_github(status_file)
            if github_content:
                try:
                    data = json.loads(github_content)
                    already_sent = data.get("exhausted_notification_sent", False)
                except:
                    pass
                    
        if already_sent:
            print("New leads detected. Resetting database status flag on GitHub...", flush=True)
            status_data = {"exhausted_notification_sent": False}
            try:
                with open(status_file, "w") as f:
                    json.dump(status_data, f)
                sync_csv_to_github(status_file)
            except Exception as e:
                print(f"Error resetting database status: {e}", flush=True)
