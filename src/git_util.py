import os
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def sync_csv_to_github(csv_path):
    """
    Updates the CSV on GitHub using the REST API.
    More reliable in cloud environments than GitPython.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = "LeadPitch" # Assuming the repo name
    username = "A-Generative-Slice" # Assuming the username
    
    if not github_token:
        print("GITHUB_TOKEN not set. Skipping sync.")
        return False

    try:
        # 1. Get current file data to get the 'sha' (required for updates)
        url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{csv_path}"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        get_response = requests.get(url, headers=headers)
        if get_response.status_code != 200:
            print(f"Failed to fetch file info from GitHub: {get_response.text}")
            return False
        
        file_data = get_response.json()
        sha = file_data['sha']

        # 2. Read local file and encode to base64
        with open(csv_path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")

        # 3. Update the file
        commit_message = f"Cloud Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        put_data = {
            "message": commit_message,
            "content": content,
            "sha": sha,
            "branch": "main"
        }
        
        put_response = requests.put(url, headers=headers, json=put_data)
        if put_response.status_code == 200:
            print(f"Successfully updated {csv_path} on GitHub via API.")
            return True
        else:
            print(f"Failed to update GitHub: {put_response.text}")
            return False

    except Exception as e:
        print(f"Error in GitHub API sync: {e}")
        return False
