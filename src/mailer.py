import os
import yagmail
from dotenv import load_dotenv

load_dotenv()

class Mailer:
    def __init__(self):
        self.email_user = os.getenv("SMTP_EMAIL")
        self.email_pass = os.getenv("SMTP_PASSWORD")
        
        if not self.email_user or not self.email_pass:
            print("Warning: SMTP_EMAIL or SMTP_PASSWORD not set in .env")
            self.yag = None
        else:
            try:
                self.yag = yagmail.SMTP(self.email_user, self.email_pass)
            except Exception as e:
                print(f"Failed to initialize SMTP: {e}")
                self.yag = None

    def send_email(self, to_email, subject, body):
        """
        Sends an email using yagmail.
        """
        if not self.yag:
            print(f"Skipping email to {to_email} (SMTP not configured or failed)")
            # Log the pitch for manual review
            self._log_pitch(to_email, subject, body)
            return False

        try:
            self.yag.send(
                to=to_email,
                subject=subject,
                contents=body
            )
            print(f"Email successfully sent to {to_email}")
            return True
        except Exception as e:
            print(f"Error sending email to {to_email}: {e}")
            return False

    def _log_pitch(self, to_email, subject, body):
        """Logs the pitch to a file if email sending is skipped."""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        filename = f"{log_dir}/pitch_{to_email.replace('@', '_at_')}.txt"
        with open(filename, "w") as f:
            f.write(f"To: {to_email}\n")
            f.write(f"Subject: {subject}\n\n")
            f.write(body)
        print(f"Pitch saved to {filename}")
