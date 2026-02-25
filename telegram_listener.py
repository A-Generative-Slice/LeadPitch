import requests
import time
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import github_manager
import scraper_engine

API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_telegram_msg(text):
    url = f"{API_URL}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def send_telegram_document(filepath):
    url = f"{API_URL}/sendDocument"
    try:
        with open(filepath, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': TELEGRAM_CHAT_ID}
            requests.post(url, data=data, files=files, timeout=15)
    except Exception as e:
        print(f"Failed to send Telegram document: {e}")

def get_updates(offset=None):
    url = f"{API_URL}/getUpdates"
    params = {"timeout": 100}
    if offset:
        params["offset"] = offset
        
    try:
        response = requests.get(url, params=params, timeout=110)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to get updates from Telegram: {e}")
        return None

def main():
    print("LeadPitch Local Listener started. Polling for commands...")
    offset = None
    
    while True:
        try:
            updates = get_updates(offset)
            
            if updates and updates.get("ok"):
                for update in updates.get("result", []):
                    offset = update["update_id"] + 1
                    
                    message = update.get("message", {})
                    chat_id = str(message.get("chat", {}).get("id", ""))
                    text = message.get("text", "")
                    
                    if chat_id != str(TELEGRAM_CHAT_ID):
                        print(f"Unauthorized access attempt from chat ID: {chat_id}")
                        continue
                        
                    if text and text.startswith("/prompt"):
                        parts = text.split(" ", 2)
                        if len(parts) < 3:
                            send_telegram_msg("⚠️ Format error. Use: /prompt [number] [niche]")
                            continue
                            
                        try:
                            target_count = int(parts[1])
                        except ValueError:
                            send_telegram_msg("⚠️ Format error: count must be a number. Use: /prompt [number] [niche]")
                            continue
                            
                        niche_query = parts[2].strip()
                        
                        send_telegram_msg(f"🎯 Target locked. Hunting for {target_count} leads in niche: {niche_query}.")
                        
                        github_manager.pull_latest()
                        
                        existing_emails = github_manager.load_existing_emails()
                        print(f"Currently tracking {len(existing_emails)} existing emails.")
                        
                        final_leads_count = scraper_engine.process_target(
                            niche_query, 
                            existing_emails, 
                            target_count, 
                            send_telegram_msg
                        )
                        
                        github_manager.push_updates(niche_query)
                        
                        # Send the actual CSV file directly to Telegram
                        send_telegram_document("clients.csv")
                        
                        send_telegram_msg(f"✅ LeadPitch Complete. Final tally: {final_leads_count}/{target_count} leads for {niche_query}. CSV synced to GitHub and attached above.")
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("Shutting down LeadPitch listener.")
            break
        except Exception as e:
            print(f"Unexpected error in polling loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
