import os
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def _get_repo_info():
    """Helper to get repo owner and name dynamically."""
    full_repo = os.getenv("GITHUB_REPOSITORY") # "owner/repo" in Actions
    if full_repo and "/" in full_repo:
        username, repo_name = full_repo.split("/")
        return username, repo_name
    return "A-Generative-Slice", "LeadPitch"

def sync_csv_to_github(csv_path):
    """
    Updates the CSV on GitHub using the REST API.
    More reliable in cloud environments than GitPython.
    """
    github_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    username, repo_name = _get_repo_info()
    
    if not github_token:
        print("DEBUG: GITHUB_TOKEN not set. Real-time API sync skipped.", flush=True)
        return False

    try:
        url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{csv_path}"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        get_response = requests.get(url, headers=headers)
        if get_response.status_code != 200:
            print(f"DEBUG: Failed to fetch file info for {csv_path}: {get_response.status_code}", flush=True)
            return False
        
        file_data = get_response.json()
        sha = file_data['sha']

        with open(csv_path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")

        commit_message = f"Cloud Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [skip ci]"
        put_data = {
            "message": commit_message,
            "content": content,
            "sha": sha,
            "branch": "main"
        }
        
        put_response = requests.put(url, headers=headers, json=put_data)
        if put_response.status_code in [200, 201]:
            print(f"✅ Real-time sync: {csv_path} updated on GitHub.", flush=True)
            return True
        else:
            print(f"❌ API Sync Failed ({put_response.status_code}): {put_response.text}", flush=True)
            return False

    except Exception as e:
        print(f"DEBUG: Error in API sync: {e}", flush=True)
        return False

def send_github_notification(status="OFFLINE"):
    """
    Creates an issue on GitHub to trigger a push notification to the user's phone.
    """
    github_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    username, repo_name = _get_repo_info()
    
    if not github_token:
        return

    url = f"https://api.github.com/repos/{username}/{repo_name}/issues"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    title = f"🔴 LeadPitch Status: {status}"
    body = f"Alert: The LeadPitch automation process has entered state: {status}.\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    data = {"title": title, "body": body}
    try:
        requests.post(url, headers=headers, json=data)
        print(f"Notification Sent: {status}", flush=True)
    except:
        pass

def clear_github_notifications():
    """
    Closes any open 'Offline' issues to keep the notification list clean.
    """
    github_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    username, repo_name = _get_repo_info()
    
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
            print("Cleared previous status notifications.", flush=True)
    except:
        pass
