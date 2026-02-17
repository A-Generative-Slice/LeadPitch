import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class PitchAgent:
    # Fallback chain of free OpenRouter models (tried in order)
    FREE_FALLBACK_MODELS = [
        "google/gemini-2.0-flash-001",
        "meta-llama/llama-3.3-8b-instruct:free",
        "qwen/qwen3-8b:free",
        "mistralai/mistral-small-3.1-24b-instruct:free",
        "google/gemma-3-4b-it:free",
    ]

    def __init__(self):
        # OpenRouter uses the OpenAI SDK with a custom base URL
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("CRITICAL ERROR: OPENROUTER_API_KEY is missing! Pitch generation will fail.", flush=True)
            self.client = None
        else:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
        self.primary_model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
        self.company_name = os.getenv("COMPANY_NAME", "Generative Slice")

    def generate_pitch(self, client_data):
        """
        Generates a hyper-personalized, professional pitch email.
        """
        client_name = client_data.get('Client Name', '')
        company_name_lead = client_data.get('Client Name', 'your organization')
        theme = client_data.get('Theme of Business', 'N/A')
        pain_points = client_data.get('Pain Points', 'N/A')
        possible_solution = client_data.get('Possible Solution', 'N/A')
        
        # Decide on a natural salutation
        if client_name and any(word in client_name for word in ["Boutique", "Shop", "Stall", "Market", "Patissiere"]):
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
        1. NO MARKDOWN BOLDING. Do NOT use **stars** for emphasis anywhere in the email.
        2. NO PLACEHOLDERS. Never use brackets like [Your Name], [Contact Person Name], [Your Phone Number], or [Subject].
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

        # Build the model fallback chain: primary first, then free alternatives
        import time as _time
        models_to_try = [self.primary_model]
        for m in self.FREE_FALLBACK_MODELS:
            if m != self.primary_model:
                models_to_try.append(m)

        for model in models_to_try:
            try:
                print(f"   🔄 Trying model: {model}", flush=True)
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a professional B2B outreach expert. You write clean, plain-text style emails without ANY markdown symbols or placeholders. Everything you output must be the final text."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=400
                )
                content = response.choices[0].message.content.strip()
                
                # Remove any stray markdown artifacts if the AI slips up
                content = content.replace("**", "")

                # Split into subject and body
                lines = content.split('\n', 1)
                subject = "Discovery for " + company_name_lead
                body = content

                if "Subject:" in lines[0]:
                    subject = lines[0].replace("Subject:", "").strip()
                    body = lines[1].strip() if len(lines) > 1 else ""

                # Final safety check to remove placeholders if AI ignores instructions
                placeholders = ["[Your Name]", "[Contact Person Name]", "[Your Phone Number]", "[Subject]", "[Name]"]
                for p in placeholders:
                    body = body.replace(p, "Mohammad Hussain" if "Name" in p else "93441 15330")

                print(f"   ✅ Pitch generated via {model}", flush=True)
                return subject, body

            except Exception as e:
                print(f"   ⚠️ {model} failed: {e}", flush=True)
                _time.sleep(5)  # Brief pause before trying next model
                continue

        print(f"❌ All models failed for {company_name_lead}.", flush=True)
        return None, None
