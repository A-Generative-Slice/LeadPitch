# 🦅 LeadPitch

**AI-powered sales pitches that don't sound like they were written by a blender.**

LeadPitch is a lightweight, set-it-and-forget-it automation for sending professional, highly-personalized outreach emails. It drips out one email every 10 minutes so you don't get flag-shamed by spam filters or hit your AI quotas too fast.

## 💅 The Vibe
- **No Markdown in your emails**: Because real humans don't send emails with triple backticks and bold headers.
- **10-minute Drip**: Smooth like butter. One lead at a time.
- **Auto-Sync**: Updates your `clients.csv` on GitHub every time it sends a mail. You can track your progress while drinking a latte.
- **Cloud-Ready**: Native support for Railway so it runs while you sleep.

## 🚀 Speedrun Setup
1. Fill `clients.csv` with your leads.
2. Toss your keys into `.env`.
3. Run the scheduler:
   ```bash
   python3 main.py --schedule
   ```

## 🌩️ Deployment
If you want to run this in the cloud (Railway style), check out the [RAILWAY_GUIDE.md](./RAILWAY_GUIDE.md). It's basically magic.

---
*Built with ❤️ and a bit too much caffeine by A Generative Slice.*
