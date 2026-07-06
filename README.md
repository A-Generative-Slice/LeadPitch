# 🦅 LeadPitch: Hyper-Personalized Outreach (Cloud Edition)

**Turning cold leads into warm conversations using AI that actually "gets it."**

LeadPitch is an automated sales assistant that lives in your cloud. It generates personalized, human-sounding pitches using **Gemini 2.0 Flash** and sends them via your own Gmail—avoiding spam filters and ensuring 100% authenticity.

## 🏎️ New Workflow: "Full Pilot"
We've moved beyond manual scripts. LeadPitch now runs on **GitHub Actions**, meaning it works while you sleep.

- **Cloud-Native Automation**: Runs every **15 minutes** automatically via GitHub Actions in Turbo Batch Mode.
- **🔍 Auto-Diagnostic**: Built-in secret verification ensures your keys are always set correctly.
- **💾 Real-Time Sync**: Every email sent is immediately synced back to `clients.csv` in your repository.
- **🚀 High-Volume Target**: **Turbo Batch Mode** sends up to 25 emails per run (with 30s safety gaps), reliably achieving your **300 emails per day** target.

## 🚀 Getting Started

### 1. Configure Secrets
Add your API keys and SMTP credentials to your repository secrets (**Settings > Secrets and variables > Actions**). See the [Configuration Guide](./CODESPACES_GUIDE.md) for details.

### 2. Manual Trigger
1. Go to the **Actions** tab in this repo.
2. Select **"🦅 LeadPitch: Automated Outreach"**.
3. Click **Run workflow** -> **Branch: main** -> **Run workflow**.

### 3. Track Status
- Open [clients.csv](./clients.csv) to see "Sent Status" change to **Yes** in real-time.
- Check your Gmail "Sent" folder to see the actual pitches!

## ✨ Key Features
- **Zero Markdown**: Output is pure, clean text. No backticks or robotic placeholders.
- **Smart Mapping**: Maps Industry, Pain Points, and Location into unique, contextual hooks.
- **Low Credit Friendly**: Optimization for low-budget API usage (1000 token limit per request).

## 🛠️ Tech Stack
- **Brain**: OpenRouter (Gemini 2.0 Flash)
- **Engine**: Python 3.10+ + Pandas
- **Automation**: GitHub Actions (CI/CD)
- **Outreach**: SMTP (Gmail App Passwords)

---
*Built for the bold by **A Generative Slice**.*
