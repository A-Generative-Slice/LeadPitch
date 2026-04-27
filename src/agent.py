import os
import time as _time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class PitchAgent:
    def __init__(self):
        # primary: GitHub Models (using GITHUB_TOKEN)
        # fallback: OpenRouter (using OPENROUTER_API_KEY)
        
        self.github_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        
        self.github_client = None
        if self.github_token:
            self.github_client = OpenAI(
                base_url="https://models.inference.ai.azure.com",
                api_key=self.github_token
            )
            print("✅ GitHub Models initialized (using Student/Pro subscription).", flush=True)
        
        self.openrouter_client = None
        if self.openrouter_key:
            self.openrouter_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_key
            )
        
        # GitHub Models availability (free for Student/Pro)
        self.github_models = [
            "gpt-4o-mini",
            "meta-llama-3.1-70b-instruct",
            "meta-llama-3.1-8b-instruct",
            "phi-3.5-moe-instruct"
        ]
        
        # OpenRouter fallback models
        self.openrouter_models = [
            "meta-llama/llama-3.3-70b-instruct:free",
            "mistralai/mistral-small-3.1-24b-instruct:free",
            "google/gemma-3-27b-it:free"
        ]
        
        self.company_name = os.getenv("COMPANY_NAME", "A Generative Slice")

    def generate_pitch(self, client_data):
        """
        Generates a hyper-personalized, professional pitch email using GitHub Models or OpenRouter.
        """
        client_name = client_data.get('Client Name', '')
        company_name_lead = client_data.get('Client Name', 'your organization')
        theme = client_data.get('Business Theme', 'N/A')
        pain_points = client_data.get('Pain Points', 'N/A')
        possible_solution = client_data.get('Possible Solution', 'N/A')
        
        # Decide on a natural salutation
        if client_name and any(word in str(client_name) for word in ["Boutique", "Shop", "Stall", "Market", "Patissiere"]):
             salutation = f"Dear the {client_name} Team,"
        elif client_name:
             salutation = f"Dear {client_name},"
        else:
             salutation = "Dear Team,"

        prompt = f"""
        You are Mohammad Hussain, the founder of A Generative Slice, an AI automation firm.
        Write a hyper-personalized, professional sales pitch email.

        Client Details:
        - Company/Client Name: {company_name_lead}
        - Business Theme: {theme}
        - Their Pain Points: {pain_points}
        - Our Proposed Solution: {possible_solution}

        CRITICAL INSTRUCTIONS:
        1. NO MARKDOWN BOLDING. Do NOT use **stars** for emphasis.
        2. NO PLACEHOLDERS. Never use brackets like [Your Name].
        3. SALUTATION: Use "{salutation}".
        4. BRANDING: Our company is "A Generative Slice".
        5. SIGNATURE: End the email exactly like this:
           
           Best regards,
           
           Mohammad Hussain
           Founder, A Generative Slice
           Contact: 93441 15330

        Structure:
        - Subject Line: Professional and relevant to their business.
        - Body: Empathize with their {theme} and {pain_points}. Propose {possible_solution}.
        - CTA: Ask for a brief 10-minute call.

        Format:
        Subject: [Write the actual subject here]
        [Write the actual email body here]
        """

        # Try GitHub Models first (Free for user)
        if self.github_client:
            for model in self.github_models:
                try:
                    print(f"   🔄 Trying GitHub Model: {model}", flush=True)
                    response = self.github_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a professional B2B outreach expert. You write clean, plain-text style emails without ANY markdown symbols or placeholders."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=400
                    )
                    return self._parse_response(response.choices[0].message.content, company_name_lead, model)
                except Exception as e:
                    print(f"   ⚠️ GitHub {model} failed: {e}", flush=True)
                    _time.sleep(2)
                    continue

        # Fallback to OpenRouter
        if self.openrouter_client:
            for model in self.openrouter_models:
                try:
                    print(f"   🔄 Falling back to OpenRouter: {model}", flush=True)
                    response = self.openrouter_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a professional B2B outreach expert."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=400
                    )
                    return self._parse_response(response.choices[0].message.content, company_name_lead, model)
                except Exception as e:
                    print(f"   ⚠️ OpenRouter {model} failed: {e}", flush=True)
                    _time.sleep(2)
                    continue

        print(f"❌ All AI models failed for {company_name_lead}.", flush=True)
        return None, None

    def _parse_response(self, content, company_name_lead, model_name):
        content = content.strip().replace("**", "")
        lines = content.split('\n', 1)
        subject = f"Discovery for {company_name_lead}"
        body = content

        if "Subject:" in lines[0]:
            subject = lines[0].replace("Subject:", "").strip()
            body = lines[1].strip() if len(lines) > 1 else ""

        # Cleanup placeholders
        placeholders = ["[Your Name]", "[Contact Person Name]", "[Your Phone Number]", "[Subject]", "[Name]"]
        for p in placeholders:
            body = body.replace(p, "Mohammad Hussain" if "Name" in p else "93441 15330")

        print(f"   ✅ Pitch generated via {model_name}", flush=True)
        return subject, body

