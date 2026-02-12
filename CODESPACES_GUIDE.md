# 🛰️ Launching LeadPitch in Codespaces

GitHub Codespaces is the ultimate home for LeadPitch. It bypasses cloud blocks and lets you use your personal Gmail account securely.

### 1. 🔑 Configure your Secrets (Crucial)
GitHub handles your keys so you don't have to worry about `.env` files.
1.  In your Repo, go to **Settings** -> **Secrets and variables** -> **Codespaces**.
2.  Add these **New repository secrets**:
    - `OPENROUTER_API_KEY`: Your key from OpenRouter.
    - `GH_TOKEN`: Your GitHub Personal Access Token (for auto-sync).
    - `SMTP_EMAIL`: `agenerativeslice@gmail.com`
    - `SMTP_PASSWORD`: Your 16-character Google App Password.
    - `COMPANY_NAME`: `"A Generative Slice"`
    - `OPENROUTER_MODEL`: `google/gemini-2.0-flash-001`

### 2. 🚀 Start the Engines
1.  Click the green **"<> Code"** button and create a Codespace.
2.  Once the terminal wakes up, run:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Choose your Mission**:
    - **The Marathon (Drip)**: Perfect for continuous, safe outreach.
      ```bash
      python3 main.py --schedule
      ```
    - **The Sprint (Turbo)**: Sequential sends with a 20s "human" delay.
      ```bash
      python3 main.py --all
      ```

### 🔋 Pro Tips
- **Stay Alive**: Keep the browser tab open to keep the script running.
- **Secrets**: If you add secrets *after* starting, use `Ctrl+Shift+P` -> `Full Restart`.
- **Visibility**: Watch your Gmail "Sent" folder to see the AI magic in real-time.

---
*Powered by the cloud, tuned for results.* 🦅🔥
