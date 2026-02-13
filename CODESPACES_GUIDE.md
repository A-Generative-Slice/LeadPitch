# 🛰️ Setting up LeadPitch (Secrets & Configuration)

LeadPitch is designed to run automatically on **GitHub Actions**, but it can also be run manually in **GitHub Codespaces**. Both require your secrets to be configured in your repository settings.

## 🔑 1. Configure Repository Secrets (Required)
GitHub handles your keys securely. You need to add these for the outreach to work.

1.  In your GitHub Repo, go to **Settings** -> **Secrets and variables** -> **Actions**.
2.  Click **New repository secret** for each of the following:
    - `OPENROUTER_API_KEY`: Your key from [OpenRouter](https://openrouter.ai/).
    - `GH_TOKEN`: Your GitHub Personal Access Token (with `repo` permissions).
    - `SMTP_EMAIL`: Your Gmail address (e.g., `agenerativeslice@gmail.com`).
    - `SMTP_PASSWORD`: Your 16-character [Google App Password](https://myaccount.google.com/apppasswords).
    - `COMPANY_NAME`: Your business name (e.g., `"A Generative Slice"`).
    - `OPENROUTER_MODEL`: Use `openrouter/free` to always stay on the free tier.

> [!TIP]
> **Protip**: If you also want to use **Codespaces**, add these same secrets under **Settings -> Secrets and variables -> Codespaces** as well.

## 🔍 2. The Verification Step
When you run the GitHub Action, the first thing it does is **"🔍 Verify Secrets"**. 
- Check the logs of this step to see if any keys are missing.
- ✅ = Secret found.
- ❌ = Secret missing (The workflow will print a warning but might still try to run).

## 🚀 3. Manual Execution (Codespaces)
If you want to run the script manually to test or debug:
1.  Launch a **Codespace**.
2.  Run `pip install -r requirements.txt`.
3.  **Choose your Mission**:
    - **Drip Mode**: Sequential sends with 10min delays.
      ```bash
      python3 main.py --schedule
      ```
    - **Turbo Mode**: 20s delays between sends.
      ```bash
      python3 main.py --all
      ```

## 🔋 Best Practices
- **App Passwords**: Never use your real Gmail password. Use an [App Password](https://support.google.com/accounts/answer/185833).
- **Token Limits**: The AI is currently capped at **1000 tokens** per request to save on your API credits.
- **Auto-Sync**: The system automatically commits `clients.csv` changes with the tag `[skip ci]` to prevent infinite loops.

## 🆓 4. How to Run LeadPitch for FREE
You can run this entire system without spending a cent!

1.  **Use Free Models**: In your secrets, set `OPENROUTER_MODEL` to:
    - `google/gemini-2.0-flash-exp:free` (Fast & High Quality)
    - `openrouter/free` (Auto-routes to the best available free model)
2.  **Gmail is Free**: Just use a standard Gmail account with an **App Password**.
3.  **Efficiency**: The bot is already configured to be "gentle" on free tiers by processing leads with 20-second delays and a 10-minute scheduler.

---
*Powered by the cloud, tuned for results.* 🦅🔥
