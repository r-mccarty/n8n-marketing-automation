# Social Platform Integration Plan

Research and implementation paths for expanding N8N marketing automation beyond X (Twitter).

---

## Executive Summary

| Platform | Difficulty | Cost | Auth Complexity | Recommendation |
|----------|------------|------|-----------------|----------------|
| **Discord** | Easy | Free | None (webhooks) | **Start here** |
| **Threads** | Medium | Free | OAuth (Meta) | High value, growing platform |
| **Facebook** | Medium-Hard | Free | OAuth + App Review | If you have FB Page |
| **Instagram** | Medium-Hard | Free | OAuth + Business Account | Requires FB Page link |
| **Reddit** | Hard | Free tier limited | OAuth 2.0, strict limits | Defer unless critical |

---

## 1. Discord

### Overview
Discord webhooks are the easiest integration path. No bot required, no authentication tokens to manage, just a URL that accepts POST requests.

### Requirements
- Discord server with admin access
- Channel where you want to post

### How It Works
1. Create webhook in Discord channel settings
2. POST JSON to webhook URL
3. Message appears in channel

### Implementation Path

```bash
# 1. Create webhook in Discord
# Server Settings → Integrations → Webhooks → New Webhook
# Copy webhook URL (keep secret!)

# 2. Test posting
curl -X POST "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello from N8N!"}'
```

### N8N Integration
- Use built-in **HTTP Request** node (same pattern as Tweet API)
- Or use **Discord** node with webhook URL
- No OAuth, no token refresh, no complexity

### Webhook Message Format
```json
{
  "content": "Your message here",
  "username": "OpticWorks Bot",
  "avatar_url": "https://example.com/avatar.png",
  "embeds": [{
    "title": "New Blog Post",
    "description": "Check out our latest...",
    "url": "https://optic.works/blog/post",
    "color": 5814783
  }]
}
```

### Estimated Effort
- **Setup time:** 15 minutes
- **N8N workflow:** Copy existing hourly poster, change URL
- **Maintenance:** Near zero

### Cost
**Free** - No API limits for webhooks

---

## 2. Threads (Meta)

### Overview
Meta's Threads API launched in 2024 and has matured significantly. Now supports one-step text publishing, making it nearly as simple as our Tweet API shim.

### Requirements
- Meta Developer account
- Threads account (can use existing Instagram login)
- Business verification in Meta Business Suite

### API Capabilities
- Text posts (500 char limit)
- Image posts
- Video posts
- Polls (new in July 2025)
- Webhooks for mentions

### Implementation Path

```bash
# 1. Create Meta Developer App
# https://developers.facebook.com/apps/
# Select "Business" app type
# Add "Threads API" product

# 2. Get Access Token
# App Dashboard → Threads → Generate Token
# Requires: threads_basic, threads_content_publish

# 3. Test posting
curl -X POST "https://graph.threads.net/v1.0/me/threads" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d "media_type=TEXT" \
  -d "text=Hello from automation!"
```

### N8N Integration Options

**Option A: Direct API (Recommended)**
- Use HTTP Request node
- Store access token in N8N credentials
- Token refresh every 60 days (can automate)

**Option B: Threads API Shim**
- Similar to our Tweet API shim
- Python service handles auth
- Simpler N8N workflow

### Token Management
- Short-lived: 1 hour
- Long-lived: 60 days
- Implement auto-refresh workflow in N8N

### Estimated Effort
- **Setup time:** 1-2 hours (Meta app setup, verification)
- **N8N workflow:** Medium complexity
- **Maintenance:** Token refresh automation

### Cost
**Free** - No published rate limits for posting

---

## 3. Facebook Pages

### Overview
Facebook Graph API allows automated posting to Pages you manage. Requires app review for production use, which is paused for individuals but available for businesses.

### Requirements
- Facebook Business Page
- Meta Developer account
- Business verification
- App Review approval (for `pages_manage_posts` permission)

### Key Challenge
> "App reviews are paused for individuals indefinitely, but you can still apply if you are behind a business."

This means you need a registered business entity to get production API access.

### Implementation Path

```bash
# 1. Create Meta Business App
# https://developers.facebook.com/apps/
# Select "Business" app type

# 2. Add Facebook Login product
# Configure OAuth redirect URLs

# 3. Request permissions
# pages_manage_posts - Post to Pages
# pages_read_engagement - Read insights

# 4. Submit for App Review
# Provide business documentation
# Explain use case
# Wait for approval (days to weeks)

# 5. Generate Page Access Token
# Exchange user token for page token
# Convert to long-lived token
```

### N8N Integration
- Use **Facebook Graph API** node (built-in)
- Or HTTP Request with Graph API endpoints
- Token management similar to Threads

### API Endpoint
```bash
POST https://graph.facebook.com/v18.0/{page-id}/feed
  ?message=Your post content
  &access_token=PAGE_ACCESS_TOKEN
```

### Estimated Effort
- **Setup time:** 1-2 weeks (app review process)
- **N8N workflow:** Medium complexity
- **Maintenance:** Token refresh, permission renewals

### Cost
**Free** - Graph API has no usage fees

### Recommendation
Only pursue if you have a Facebook Page with active audience. The app review process is significant overhead.

---

## 4. Instagram

### Overview
Instagram uses the same Graph API as Facebook. Requires a Business or Creator account linked to a Facebook Page.

### Requirements
- Instagram Business/Creator account
- Linked Facebook Page
- Meta Developer app (same as Facebook)
- App Review approval

### Capabilities
- Feed posts (images, carousels)
- Reels
- Stories
- 25 posts per 24 hours limit
- 200 API requests per hour

### Limitations
- **No personal accounts** - Must be Business account
- JPEG images only
- No Instagram Live or IGTV
- No shopping tags or branded content tags

### Implementation Path
```bash
# 1. Convert to Business Account
# Instagram Settings → Account → Switch to Professional Account

# 2. Link to Facebook Page
# Instagram Settings → Account → Linked Accounts → Facebook

# 3. Same Meta App as Facebook
# Add Instagram Graph API product
# Request instagram_content_publish permission

# 4. Container-based Publishing
# Step 1: Create media container
POST https://graph.facebook.com/v18.0/{ig-user-id}/media
  ?image_url=https://example.com/image.jpg
  &caption=Your caption

# Step 2: Publish container
POST https://graph.facebook.com/v18.0/{ig-user-id}/media_publish
  ?creation_id={container-id}
```

### N8N Integration
- Two-step workflow (create container → publish)
- Use HTTP Request nodes
- Monitor container status before publishing

### Estimated Effort
- **Setup time:** Same as Facebook (1-2 weeks)
- **N8N workflow:** Higher complexity (async container processing)
- **Maintenance:** Token refresh, rate limit handling

### Cost
**Free** - Same Graph API as Facebook

### Recommendation
Good synergy if already doing Facebook. The Business account requirement and container-based publishing add complexity.

---

## 5. Reddit

### Overview
Reddit's API underwent significant changes in 2023, introducing paid tiers and stricter requirements. The free tier has limitations but may work for basic use cases.

### Requirements
- Reddit account
- Registered app in Reddit preferences
- OAuth 2.0 implementation
- Strict rate limit compliance

### Free Tier Limits
- 100 requests/minute with OAuth
- 10 requests/minute without OAuth
- Tokens expire every hour
- Must comply with content policies

### Commercial Use
- Enterprise agreement required
- Starts at ~$12,000/year
- Contact sales for custom pricing

### Implementation Challenges
1. **Hourly token refresh** - Access tokens expire every 60 minutes
2. **Subreddit rules** - Each subreddit has different posting rules
3. **Karma requirements** - Many subreddits require minimum karma
4. **Anti-spam measures** - Automated posting often flagged
5. **Rate limits** - Must implement backoff strategies

### Implementation Path (Free Tier)
```bash
# 1. Create Reddit App
# https://www.reddit.com/prefs/apps
# Select "script" type for personal use

# 2. Get OAuth Token
curl -X POST "https://www.reddit.com/api/v1/access_token" \
  -u "CLIENT_ID:CLIENT_SECRET" \
  -d "grant_type=password&username=USER&password=PASS"

# 3. Submit Post
curl -X POST "https://oauth.reddit.com/api/submit" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d "sr=subreddit&kind=self&title=Title&text=Content"
```

### Risks
- Account suspension for "spam"
- API access revocation
- Community backlash against bots

### Estimated Effort
- **Setup time:** 2-4 hours
- **N8N workflow:** High complexity (token refresh, error handling)
- **Maintenance:** High (token refresh, subreddit rule changes)

### Cost
- **Free tier:** Limited but usable for low volume
- **Commercial:** $12,000+/year

### Recommendation
**Defer** unless Reddit is critical to your marketing strategy. High complexity, low reliability, and risk of account issues make this a poor early investment.

---

## Recommended Implementation Order

### Phase 1: Quick Wins (This Week)
1. **Discord** - 15 minutes to full automation
   - Create webhook
   - Clone hourly poster workflow
   - Done

### Phase 2: Meta Ecosystem (Next Month)
2. **Threads** - Growing platform, simpler than FB/IG
   - Create Meta Developer app
   - Get business verification
   - Build Threads API shim or direct integration

### Phase 3: If Needed (Future)
3. **Facebook/Instagram** - Only if you have active Pages
   - Leverage same Meta app from Threads
   - Complete App Review process
   - Build container-based workflows

### Phase 4: Evaluate
4. **Reddit** - Reassess based on marketing needs
   - Consider manual posting instead
   - Or use free tier with very low volume

---

## Architecture: Multi-Platform Posting

### Option A: Platform-Specific Shims
```
N8N Workflow
    ├── Tweet API (:5680) → X
    ├── Discord Webhook → Discord
    ├── Threads API Shim (:5681) → Threads
    └── Meta Graph API → FB/IG
```

### Option B: Unified Shim Service
```
N8N Workflow → Social API Gateway (:5680)
                    ├── X (OAuth 1.0a)
                    ├── Discord (Webhook)
                    ├── Threads (OAuth 2.0)
                    └── Meta (OAuth 2.0)
```

### Option C: N8N Native (Where Possible)
```
N8N Workflow
    ├── HTTP Request → Tweet API Shim → X
    ├── HTTP Request → Discord Webhook
    ├── HTTP Request → Threads API
    └── Facebook Graph API Node → FB/IG
```

**Recommendation:** Start with Option A (current pattern), consider Option B if managing 4+ platforms.

---

## Next Steps

1. [ ] **Discord:** Create OpticWorks Discord server and webhook
2. [ ] **Threads:** Register Meta Developer app and begin verification
3. [ ] **Content Strategy:** Define what content goes to which platform
4. [ ] **Scheduling:** Determine posting frequency per platform

---

## References

### Discord
- [Intro to Webhooks - Discord](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)
- [Discord Webhooks Tutorial - Hookdeck](https://hookdeck.com/webhooks/platforms/tutorial-how-to-configure-discord-webhooks-using-the-api)

### Threads
- [Threads API: How to Post Programmatically](https://getlate.dev/blog/threads-posting-api)
- [Meta Expands Threads API - PPC Land](https://ppc.land/meta-expands-threads-api-with-advanced-features-for-developers/)
- [Setting Up Threads API - Lewis Pour](https://blog.lewisthedeveloper.com/setting-up-threads-api/)

### Facebook/Instagram
- [Instagram Graph API Guide 2025 - Elfsight](https://elfsight.com/blog/instagram-graph-api-complete-developer-guide-for-2025/)
- [Facebook API Guide 2025 - Tagembed](https://tagembed.com/blog/facebook-api/)
- [N8N Instagram/Facebook Workflow Template](https://n8n.io/workflows/5457-automate-instagram-and-facebook-posting-with-meta-graph-api-and-system-user-tokens/)

### Reddit
- [Reddit API Cost Guide 2025 - Rankvise](https://rankvise.com/blog/reddit-api-cost-guide/)
- [Reddit API Pricing - Sellbery](https://sellbery.com/blog/how-much-does-the-reddit-api-cost-in-2025/)
- [Reddit API Guide - Zuplo](https://zuplo.com/learning-center/reddit-api-guide)
