# 🦅 LeadPitch: Hyper-Personalized Outreach

**Turning cold leads into warm conversations using AI that actually "gets it."**

LeadPitch is your invisible sales assistant. It generates personalized, human-sounding pitches and drips them out from your own Gmail account—avoiding spam filters and robotic clichés.

## ✨ The Vibe
- **Pure Human**: No backticks, no markdown, no "AI-detected" formatting. Just clean text.
- **Smart Drip**: 10-minute intervals for longevity, or **Turbo Mode** for speed. 🏎️
- **Auto-Sync**: Your `clients.csv` stays updated on GitHub in real-time. Track your wins on the go.
- **Codespace Ready**: Zero setup. Launch directly in your browser and start pitching.

## 🚀 Quick Launch
1.  **Drop your Leads**: Fill `clients.csv` with your targets.
2.  **Config Secrets**: Add your keys to GitHub Codespaces (see [Guide](./CODESPACES_GUIDE.md)).
3.  **Choose your Speed**:
    - **Smooth Drip (10 min)**: `python3 main.py --schedule`
    - **Turbo Mode (20 sec)**: `python3 main.py --all`

## 🛠️ Tech Stack
- **Brain**: OpenAI / OpenRouter (Gemini 2.0 Flash)
- **Engine**: Python + Pandas
- **Outreach**: SMTP (Gmail)
- **Platform**: GitHub Codespaces

---
*Built for the bold by **A Generative Slice**.*
