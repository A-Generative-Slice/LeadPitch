import os
import time
from datetime import datetime
from git import Repo
from dotenv import load_dotenv

load_dotenv()

def sync_csv_to_github(csv_path):
    """
    Commits and pushes the updated CSV back to GitHub.
    Expected env: GITHUB_TOKEN or SSH setup.
    """
    try:
        repo_path = os.getcwd()
        repo = Repo(repo_path)
        
        # Check if there are changes
        if not repo.is_dirty(untracked_files=True):
            print("No changes to sync to GitHub.")
            return False

        repo.git.add(csv_path)
        commit_message = f"Update client send status: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        repo.index.commit(commit_message)
        
        origin = repo.remote(name='origin')
        
        # Use GITHUB_TOKEN if available for authenticated push
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            # Build the authenticated URL: https://<token>@github.com/<owner>/<repo>.git
            remote_url = origin.url
            if remote_url.startswith("https://"):
                auth_url = remote_url.replace("https://", f"https://{github_token}@")
                origin.set_url(auth_url)
                print("Using GITHUB_TOKEN for authenticated push.")
            elif remote_url.startswith("git@github.com:"):
                # If SSH, we skip token injection as it's handled by SSH keys
                print("SSH remote detected, skipping token injection.")

        origin.push()
        print(f"Successfully synced {csv_path} to GitHub.")
        return True
    except Exception as e:
        print(f"Error syncing to GitHub: {e}")
        return False
