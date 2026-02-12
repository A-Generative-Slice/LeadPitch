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

    def process_leads(self, dry_run=False):
        """
        Reads CSV, generates pitches, and sends emails for unsent leads.
        """
        try:
            df = pd.read_csv(self.csv_path)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return

        # Ensure status columns exist and handle empty/NaN
        if 'Sent Status' not in df.columns:
            df['Sent Status'] = 'No'
        df['Sent Status'] = df['Sent Status'].fillna('No')

        if 'Sent Time' not in df.columns:
            df['Sent Time'] = ''
        else:
            df['Sent Time'] = df['Sent Time'].astype(object).fillna('')

        # Find unsent leads (either 'No' or empty)
        unsent_leads = df[df['Sent Status'] == 'No']
        
        if unsent_leads.empty:
            print("No new leads to process.")
            return

        # Process only the FIRST unsent lead
        row = unsent_leads.iloc[0]
        index = unsent_leads.index[0]
        
        client_name = row.get('Client Name', 'Valued Partner')
        client_email = row.get('Email ID')

        if not client_email:
            print(f"Skipping lead at index {index}: No email provided for {client_name}")
            df.at[index, 'Sent Status'] = 'Invalid Email'
            df.to_csv(self.csv_path, index=False)
            return

        print(f"Generating pitch for {client_name}...")
        subject, body = self.agent.generate_pitch(row.to_dict())

        if not subject or not body:
            print(f"Failed to generate pitch for {client_name}. Skipping...")
            return

        if dry_run:
            print(f"--- DRY RUN: Pitch for {client_name} ---")
            print(f"To: {client_email}")
            print(f"Subject: {subject}")
            print("-" * 30)
            df.at[index, 'Sent Status'] = 'Dry Run Verified'
        else:
            success = self.mailer.send_email(client_email, subject, body)
            if success:
                df.at[index, 'Sent Status'] = 'Yes'
                df.at[index, 'Sent Time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Save progress locally
        df.to_csv(self.csv_path, index=False)
        print(f"Successfully processed {client_name}.")
        
        # Sync back to GitHub if not a dry run
        if not dry_run:
            sync_csv_to_github(self.csv_path)
