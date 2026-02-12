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
    # GitHub doesn't allow secrets to start with GITHUB_, so we use GH_TOKEN
    github_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    repo_name = "LeadPitch" 
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

def send_github_notification(status="OFFLINE"):
    """
    Creates an issue on GitHub to trigger a push notification to the user's phone.
    """
    github_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    repo_name = "LeadPitch"
    username = "A-Generative-Slice"
    
    if not github_token:
        return

    url = f"https://api.github.com/repos/{username}/{repo_name}/issues"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    title = f"🔴 LeadPitch Status: {status}"
    body = f"Alert: The LeadPitch automation process in Codespaces has entered state: {status}.\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    data = {"title": title, "body": body}
    try:
        requests.post(url, headers=headers, json=data)
        print(f"GitHub Notification Sent: {status}")
    except:
        pass

def clear_github_notifications():
    """
    Closes any open 'Offline' issues to keep the notification list clean.
    """
    github_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    repo_name = "LeadPitch"
    username = "A-Generative-Slice"
    
    if not github_token:
        return

    url = f"https://api.github.com/repos/{username}/{repo_name}/issues?state=open"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            issues = response.json()
            for issue in issues:
                if "LeadPitch Status" in issue['title']:
                    issue_url = f"https://api.github.com/repos/{username}/{repo_name}/issues/{issue['number']}"
                    requests.patch(issue_url, headers=headers, json={"state": "closed"})
            print("Cleared previous status notifications from GitHub.")
    except:
        pass
