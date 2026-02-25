import requests
from bs4 import BeautifulSoup
import re
import time
import os
import random
from config import TARGET_CSV_FILE

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

def get_random_ua():
    return random.choice(USER_AGENTS)

def fetch_search_page(niche_query, next_form_data=None):
    url = 'https://lite.duckduckgo.com/lite/'
    headers = {"User-Agent": get_random_ua()}
    
    if next_form_data:
        data = next_form_data
    else:
        data = {"q": f'{niche_query} "contact" -job', "kl": ""}
        
    try:
        response = requests.post(url, headers=headers, data=data, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching DuckDuckGo page: {e}")
        return None

def parse_companies_and_next_page(soup):
    company_urls = []
    
    for link in soup.find_all('a', class_='result-link', href=True):
        href = link['href']
        if href.startswith('http') and 'duckduckgo' not in href:
            company_urls.append(href)
            
    unique_urls = list(dict.fromkeys(company_urls))
    
    next_form_data = None
    next_form = soup.find('form', action='/lite/')
    if next_form and next_form.find('input', {'name': 's'}):
        next_form_data = {}
        for input_tag in next_form.find_all('input'):
            name = input_tag.get('name')
            value = input_tag.get('value', '')
            if name:
                next_form_data[name] = value
                
    return unique_urls, next_form_data

def clean_text(text):
    if not text: return "N/A"
    cleaned = re.sub(r'\s+', ' ', text).strip()
    return cleaned.replace(',', ';')  # Escape commas for CSV

def extract_company_data(company_url):
    print(f"Scraping Data: {company_url}")
    headers = {"User-Agent": get_random_ua()}
    data = {
        "email": None,
        "description": "N/A",
        "pain_points": "N/A",
        "solutions": "N/A"
    }
    
    try:
        response = requests.get(company_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 1. Extract Email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, response.text)
        valid_emails = [e for e in emails if not any(e.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.css', '.js', '.svg'])]
        if valid_emails:
            data["email"] = valid_emails[0]
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
            
        # 2. Extract Description (Meta Tag Fallback)
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            data["description"] = clean_text(meta_desc.get('content'))
            
        # 3. Heuristic Pain Point & Solution Extraction
        text_nodes = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
        pain_sentences = []
        solution_sentences = []
        
        pain_keywords = ['struggle', 'struggling', 'tired of', 'costly', 'slow', 'inefficient', 'problem', 'risk', 'fail', 'hard to', 'difficult', 'bottleneck']
        solution_keywords = ['we help', 'streamline', 'automate', 'faster', 'boost', 'increase', 'solution', 'empower', 'solve', 'proven', 'grow', 'scale']
        
        for node in text_nodes:
            text = node.get_text(separator=' ', strip=True).lower()
            if len(text) < 20 or len(text) > 300: # Filter out extremely short or long noisy tags
                continue
                
            # Scan for Pain Points
            if any(kw in text for kw in pain_keywords) and len(pain_sentences) < 2:
                pain_sentences.append(node.get_text(separator=' ', strip=True))
                
            # Scan for Solutions
            if any(kw in text for kw in solution_keywords) and len(solution_sentences) < 2:
                solution_sentences.append(node.get_text(separator=' ', strip=True))
                
        if pain_sentences:
            data["pain_points"] = clean_text(" | ".join(pain_sentences))
        if solution_sentences:
            data["solutions"] = clean_text(" | ".join(solution_sentences))
            
    except Exception as e:
        print(f"Skipping data extraction for {company_url} gracefully due to error: {e}")
        
    return data

def process_target(niche_query, existing_emails, target_count, telegram_callback):
    new_leads_found = 0
    pages_searched = 0
    max_pages = 5
    next_form_data = None
    
    file_exists = os.path.exists(TARGET_CSV_FILE)
    
    with open(TARGET_CSV_FILE, 'a', encoding='utf-8') as f:
        if not file_exists or os.path.getsize(TARGET_CSV_FILE) == 0:
            f.write("Client Name,Email ID,Contact Number,Source/Website Information,Theme of Business,Pain Points,Possible Solution,Sent Status,Sent Time\n")
            
        while new_leads_found < target_count and pages_searched < max_pages:
            print(f"Fetching page {pages_searched + 1} for niche: {niche_query}")
            soup = fetch_search_page(niche_query, next_form_data)
            
            if not soup:
                print("Failed to fetch search page, aborting search.")
                break
                
            company_urls, next_form_data = parse_companies_and_next_page(soup)
            
            if not company_urls:
                print("No more companies found on this page.")
                break
                
            for url in company_urls:
                if new_leads_found >= target_count:
                    break
                    
                data = extract_company_data(url)
                email = data.get("email")
                
                if email:
                    if email not in existing_emails:
                        print(f"Found NEW data lead: {email} at {url}")
                        client_name = url.split('//')[-1].split('/')[0] if '//' in url else url
                        f.write(f"{client_name},{email},N/A,{url},{data['description']},{data['pain_points']},{data['solutions']},No,\n")
                        f.flush()
                        existing_emails.add(email)
                        new_leads_found += 1
                        
                        if new_leads_found % 5 == 0 and new_leads_found < target_count:
                            telegram_callback(f"⏳ Update: Found {new_leads_found}/{target_count} enriched leads. Still hunting...")
                    else:
                        print(f"DUPLICATE email skipped: {email}")
                
                time.sleep(3)
                
            pages_searched += 1
            
            if new_leads_found >= target_count:
                break
                
            if not next_form_data:
                print("No next page available.")
                break
                
            time.sleep(5)
            
    return new_leads_found
