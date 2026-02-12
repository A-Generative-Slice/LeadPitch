# How to Deploy LeadPitch to Render 🚀

Since Render's free tier is built for web services, we've updated the code to include a tiny web server.

### 1. Preparation
- Your code is already pushed to GitHub.
- Ensure you have your environment variables ready.

### 2. Deploy to Render
1. **New Web Service**:
   - Go to [Dashboard.render.com](https://dashboard.render.com/).
   - Click **"New +"** -> **"Web Service"**.
   - Connect your `LeadPitch` repository.

2. **Settings**:
   - **Runtime**: `Docker`.
   - **Plan**: `Free`.

3. **Environment Variables**:
   In the **"Environment"** tab, add your keys from `.env`:
   - `OPENROUTER_API_KEY`
   - `SMTP_EMAIL`
   - `SMTP_PASSWORD`
   - `GITHUB_TOKEN`
   - `COMPANY_NAME`

4. **Deploy**: Click **"Create Web Service"**.

---

### ⚠️ IMPORTANT: Keep It Awake
Render's free tier puts your app to sleep after 15 minutes of inactivity. Since our emails are sent every 10 minutes, we need to keep the app "awake".

**Solution**: Use [UptimeRobot](https://uptimerobot.com/) (Free).
1. Create a free account.
2. Add a new **HTTP(s) Monitor**.
3. Point it to your Render URL (e.g., `https://leadpitch.onrender.com`).
4. Set the monitoring interval to **every 5 or 10 minutes**.

This will "ping" your app, keeping the 10-minute email automation running consistently! 🦅
