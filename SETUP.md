# Complete Setup Guide

Step-by-step instructions to deploy N8N Marketing Automation from scratch.

## Prerequisites

- SSH access to N100 host (`ssh n100`)
- Docker and Docker Compose on N100
- Cloudflare account with `optic.works` domain
- X Developer account with API credentials

---

## Step 1: Deploy N8N

```bash
# SSH to N100
ssh n100

# Create directory
sudo mkdir -p /opt/n8n/data
sudo chown -R 1000:1000 /opt/n8n/data

# Clone repo
cd /opt/n8n
sudo git clone https://github.com/r-mccarty/n8n-marketing-automation.git .

# Create environment file
sudo tee .env << 'EOF'
N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)
N8N_AUTH_USER=admin
N8N_AUTH_PASSWORD=your-secure-password
EOF

# Start N8N
docker compose up -d

# Verify it's running
docker compose logs -f
```

---

## Step 2: Configure Cloudflare Tunnel

Add N8N to your cloudflared config:

```bash
sudo nano /etc/cloudflared/config.yml
```

Add this ingress rule (before the catch-all):

```yaml
ingress:
  # ... existing rules ...
  - hostname: n8n.optic.works
    service: http://localhost:5678
  - service: http_status:404
```

Add DNS record:

```bash
# Via Cloudflare API
curl -X POST "https://api.cloudflare.com/client/v4/zones/YOUR_ZONE_ID/dns_records" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "CNAME",
    "name": "n8n",
    "content": "YOUR_TUNNEL_ID.cfargotunnel.com",
    "proxied": true
  }'
```

Restart cloudflared:

```bash
sudo systemctl restart cloudflared
```

---

## Step 3: Deploy Tweet API Shim

```bash
# Install Python dependencies
sudo pip3 install requests requests-oauthlib --break-system-packages

# Copy script
sudo cp /opt/n8n/scripts/tweet-api.py /opt/n8n/

# Install systemd service
sudo cp /opt/n8n/scripts/tweet-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now tweet-api

# Verify it's running
sudo systemctl status tweet-api
```

Test the API:

```bash
curl -X POST http://127.0.0.1:5680 \
  -H "Content-Type: application/json" \
  -d '{"text": "Test tweet from API"}'
```

---

## Step 4: Setup N8N

1. Open https://n8n.optic.works
2. Create your admin account (first-time setup)
3. Import the workflow:
   - Go to Workflows → Import from File
   - Select `workflows/hourly-x-poster.json`
   - Or import via CLI:
     ```bash
     docker exec n8n n8n import:workflow --input=/home/node/.n8n/workflow.json
     ```

---

## Step 5: Activate Workflow

1. Open the "Hourly X Poster (Simple)" workflow
2. Click **Test Workflow** to verify it works
3. Toggle **Active** to enable the schedule

---

## Verification Checklist

- [ ] N8N accessible at https://n8n.optic.works
- [ ] Tweet API running: `sudo systemctl status tweet-api`
- [ ] Test tweet posts successfully
- [ ] Workflow activated in N8N

---

## Updating Credentials

If you need to change X API credentials:

1. Edit `/opt/n8n/tweet-api.py`
2. Update the credential variables (or set environment variables)
3. Restart: `sudo systemctl restart tweet-api`

---

## Troubleshooting

### N8N not accessible
```bash
docker compose logs n8n
sudo systemctl status cloudflared
```

### Tweet API not responding
```bash
sudo systemctl status tweet-api
sudo journalctl -u tweet-api -f
```

### Rate limiting
- Free tier: 1,500 tweets/month
- Hourly posting uses ~720/month
- Check response for `429 Too Many Requests`

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Cloudflare Tunnel                          │
│                  n8n.optic.works → :5678                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      N100 Host                               │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   N8N (Docker)  │───▶│     Tweet API Shim (:5680)      │ │
│  │    Port 5678    │    │   Python + OAuth1 signing       │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
│                                        │                     │
└────────────────────────────────────────│─────────────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │    X API v2         │
                              │  api.twitter.com    │
                              └─────────────────────┘
```
