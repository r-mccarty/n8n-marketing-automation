# X (Twitter) API Setup Guide

This guide walks you through creating an X Developer account and obtaining API credentials for automated posting.

## Cost Summary

| Tier | Monthly Cost | Tweet Limit | Features |
|------|--------------|-------------|----------|
| **Free** | $0 | 1,500/month | Write-only, basic automation |
| Basic | $200 | 10,000/month | Read + write, analytics |
| Pro | $5,000 | 1M/month | Full access |

**We're using Free tier** - sufficient for hourly posting (~720 tweets/month).

---

## Step 1: Create X Account for OpticWorks

1. Go to https://twitter.com/signup
2. Use optic.works brand email
3. Choose a handle (e.g., `@opticworks`, `@optic_works`, `@opticworksio`)
4. Complete profile setup with:
   - Profile picture (OpticWorks logo)
   - Bio describing the brand
   - Website link to optic.works

---

## Step 2: Apply for Developer Account

1. Go to https://developer.twitter.com/
2. Click "Sign up" or "Developer Portal"
3. Sign in with the OpticWorks X account

### Developer Application Form

When prompted, provide:

**Use Case:**
- Select: "Hobbyist" → "Making a bot"

**Description (example):**
```
Building an automated marketing bot for OpticWorks, a hardware and smart home
technology company. The bot will post scheduled content about our products,
technical articles, and company updates. We plan to post hourly updates about
hardware projects, IoT, and smart home automation.
```

**How will you use the API:**
```
We will use the X API to:
1. Post automated tweets on a schedule (hourly)
2. Share links to our blog and product pages
3. Engage with our community through automated content

We will NOT:
- Spam or post misleading content
- Aggregate or sell data
- Influence elections or political campaigns
```

4. Accept the Developer Agreement
5. Verify your email

---

## Step 3: Create an App

1. In Developer Portal, go to **Projects & Apps**
2. Click **+ Add App** or create a new project
3. Name your app: `OpticWorks Marketing Bot`

### Configure App Permissions

**Critical:** Set permissions to "Read and Write"

1. Go to your app settings
2. Find **User authentication settings**
3. Click **Set up**
4. Configure:
   - **App permissions:** Read and Write
   - **Type of App:** Web App, Automated App or Bot
   - **Callback URL:** `https://n8n.optic.works/rest/oauth2-credential/callback`
   - **Website URL:** `https://optic.works`

5. Save changes

---

## Step 4: Generate API Credentials

### Keys and Tokens Tab

1. Go to your app's **Keys and tokens** tab
2. Generate/Regenerate:

**API Key and Secret (Consumer Keys):**
```
API Key: xxxxxxxxxxxxxxxxxxxx
API Key Secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Access Token and Secret:**
```
Access Token: xxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Access Token Secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> **Important:** After changing permissions, you MUST regenerate your Access Token and Secret for the changes to take effect.

---

## Step 5: Store Credentials

Add these to Infisical (or your `.env` file):

```bash
X_API_KEY=your-api-key
X_API_SECRET=your-api-secret
X_ACCESS_TOKEN=your-access-token
X_ACCESS_SECRET=your-access-token-secret
```

---

## Step 6: Configure in N8N

1. Open N8N: https://n8n.optic.works
2. Go to **Credentials** → **Add Credential**
3. Search for "X" or "Twitter"
4. Select **X OAuth API**
5. Enter:
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret
6. Click **Save**

---

## Troubleshooting

### "Unauthorized" Error
- Regenerate Access Token after changing permissions
- Ensure app has "Read and Write" permissions

### "Rate Limit Exceeded"
- Free tier: 1,500 tweets/month
- Wait for rate limit reset (usually 15 minutes for short-term limits)

### "Forbidden" Error
- Check that the account isn't suspended
- Verify developer app is approved
- Ensure you're using OAuth 1.0a (not OAuth 2.0) for posting

---

## API Limits (Free Tier)

| Endpoint | Limit |
|----------|-------|
| Tweet creation | 1,500/month |
| Rate limit window | 15 minutes |
| Per-window limit | ~50 tweets |

Hourly posting = 24/day = ~720/month (well within limit)
