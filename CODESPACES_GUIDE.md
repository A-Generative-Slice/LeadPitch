# How to Run LeadPitch in GitHub Codespaces 🛰️

Running in GitHub Codespaces is a great way to use your personal Gmail account without cloud provider blocks. Follow these steps to get your automation running.

### 1. Launch Codespaces
1.  Go to your GitHub repository: [A-Generative-Slice/LeadPitch](https://github.com/A-Generative-Slice/LeadPitch).
2.  Click the green **"<> Code"** button.
3.  Select the **"Codespaces"** tab and click **"Create codespace on main"**.

### 2. Configure Environment Variables
GitHub Codespaces handles secrets securely. You don't need a `.env` file!
1.  In your GitHub repository, go to **Settings** -> **Secrets and variables** -> **Codespaces**.
2.  Click **"New repository secret"** for each of these:
    - `OPENROUTER_API_KEY`: (Your sk-or-... key)
    - `OPENROUTER_MODEL`: `google/gemini-2.0-flash-001`
    - `SMTP_EMAIL`: (Your Gmail address)
    - `SMTP_PASSWORD`: (Your 16-character App Password)
    - `COMPANY_NAME`: `"A Generative Slice"`
    - `GITHUB_TOKEN`: (Your ghp_... token)

*(Note: If you already have the Codespace open, you'll need to restart it for these secrets to take effect.)*

### 3. Start the Automation
Once the Codespace terminal is ready:
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Start the bot:
    ```bash
    python3 main.py --schedule
    ```

### 4. Keep it Running 🔋
- **Activity**: The Codespace will stay active as long as you have the tab open.
- **Manual Restart**: If it times out, simply open the repository again, go to the Codespaces tab, and resume your existing Codespace.
- **Monitoring**: You will see the logs (Generating pitch, Email sent, etc.) directly in the terminal!

---
> [!TIP]
> You can also open your Codespace in the **VS Code Desktop app**. This is often more stable for long-running scripts than a browser tab.
