import os
import resend
from dotenv import load_dotenv

load_dotenv()

class Mailer:
    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY")
        if not self.api_key:
            print("Warning: RESEND_API_KEY not set in .env")
        else:
            resend.api_key = self.api_key
            
    def send_email(self, to_email, subject, body):
        """
        Sends an email using Resend API.
        NOTE: Onboarding allows sending only to the account owner (agenerativeslice@gmail.com)
        until a domain is verified.
        """
        if not self.api_key:
            print(f"Skipping email to {to_email} (RESEND_API_KEY not set)")
            self._log_pitch(to_email, subject, body)
            return False

        try:
            params = {
                "from": "LeadPitch <onboarding@resend.dev>",
                "to": [to_email],
                "subject": subject,
                "text": body,
            }
            
            r = resend.Emails.send(params)
            print(f"Email sent successfully to {to_email} via Resend. ID: {r['id']}")
            return True
        except Exception as e:
            print(f"Error sending email to {to_email} via Resend: {e}")
            # If it's a domain verification error, we still log it
            self._log_pitch(to_email, subject, body)
            return False

    def _log_pitch(self, to_email, subject, body):
        """Logs the pitch to a file if email sending is skipped or fails."""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        filename = f"{log_dir}/pitch_{to_email.replace('@', '_at_')}.txt"
        with open(filename, "w") as f:
            f.write(f"To: {to_email}\n")
            f.write(f"Subject: {subject}\n\n")
            f.write(body)
        print(f"Pitch saved to {filename}")
