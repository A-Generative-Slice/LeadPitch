# How to Deploy LeadPitch to Railway 🚀

Railway is the best platform for this project because it supports background schedulers without putting them to sleep on the free/trial tier.

### 1. Preparation
- Ensure your code is pushed to a **private** GitHub repository.
- Generate a [GitHub Personal Access Token (Fine-grained)](https://github.com/settings/personal-access-tokens/new).
  - Give it **Read and Write** access to 'Contents'.
  - Copy the token.

### 2. Deploy to Railway
1. **Connect Repository**: 
   - Go to [Railway.app](https://railway.app/).
   - Click "New Project" -> "Deploy from GitHub repo".
   - Select your `LeadPitch` repository.

2. **Set Environment Variables**:
   In the Railway dashboard, go to the **Variables** tab and add the following:
   - `OPENROUTER_API_KEY`: Your OpenRouter key.
   - `RESEND_API_KEY`: The key from Resend (re_...).
   - `GITHUB_TOKEN`: Your GitHub token.
   - `COMPANY_NAME`: "A Generative Slice"

3. **Deploy**:
   - Railway will automatically detect the `Dockerfile` and start your 10-minute drip automation.
   - Check the **View Logs** tab to watch your first email go out!

---
> [!TIP]
> Your `clients.csv` will automatically sync back to GitHub after every email is sent. You can monitor progress by simply opening the file on GitHub!
