import pandas as pd
from datetime import datetime
from src.agent import PitchAgent
from src.mailer import Mailer
from src.git_util import sync_csv_to_github

class LeadProcessor:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.agent = PitchAgent()
        self.mailer = Mailer()

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

        unsent_leads = df[df['Sent Status'] == 'No']
        
        if unsent_leads.empty:
            print("No new leads to process.", flush=True)
            return

        leads_to_process = unsent_leads if all_leads else unsent_leads.iloc[:1]
        
        for index, row in leads_to_process.iterrows():
            client_name = row.get('Client Name', 'Valued Partner')
            client_email = row.get('Email ID')

            if not client_email:
                print(f"Skipping lead at index {index}: No email provided for {client_name}", flush=True)
                df.at[index, 'Sent Status'] = 'Invalid Email'
                df.to_csv(self.csv_path, index=False)
                continue

            print(f"Generating pitch for {client_name}...", flush=True)
            subject, body = self.agent.generate_pitch(row.to_dict())

            if not subject or not body:
                print(f"Failed to generate pitch for {client_name}. Skipping...", flush=True)
                continue

            if dry_run:
                print(f"--- DRY RUN: Pitch for {client_name} ---", flush=True)
                df.at[index, 'Sent Status'] = 'Dry Run Verified'
            else:
                success = self.mailer.send_email(client_email, subject, body)
                if success:
                    df.at[index, 'Sent Status'] = 'Yes'
                    df.at[index, 'Sent Time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Save progress locally
            df.to_csv(self.csv_path, index=False)
            print(f"Successfully processed {client_name}.", flush=True)
            
            # Sync back to GitHub if not a dry run
            if not dry_run:
                sync_csv_to_github(self.csv_path)

            if all_leads and index != leads_to_process.index[-1]:
                delay = 20 # 20 second gap between emails
                print(f"Waiting {delay} seconds for next lead to avoid spam flags...", flush=True)
                time.sleep(delay)
