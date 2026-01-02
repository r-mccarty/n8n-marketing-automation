# N8N Marketing Automation

N8N-powered marketing automation platform for OpticWorks. Self-hosted on N100 with Cloudflare tunnel access.

## Quick Links

- **N8N Dashboard:** https://n8n.optic.works
- **X (Twitter):** [@ry_mccarty](https://twitter.com/ry_mccarty)
- **GitHub:** https://github.com/r-mccarty/n8n-marketing-automation

## Overview

This repo contains:
- Docker Compose configuration for N8N deployment
- Tweet API shim service for X OAuth signing
- Exported workflows for marketing automation
- Complete documentation for setup and configuration

> **New here?** See [SETUP.md](SETUP.md) for step-by-step deployment instructions.

## Deployment

### Prerequisites
- Docker and Docker Compose on N100 host
- Cloudflare tunnel configured for `optic.works` domain
- X Developer account with API credentials

### Deploy to N100

```bash
# SSH to N100
ssh n100

# Create directory
sudo mkdir -p /opt/n8n
cd /opt/n8n

# Copy files (or clone repo)
git clone https://github.com/r-mccarty/n8n-marketing-automation.git .

# Create .env from example
cp .env.example .env
# Edit .env with your credentials

# Start N8N
docker compose up -d

# Check logs
docker compose logs -f
```

### Access N8N

Once deployed and Cloudflare tunnel is configured:
- URL: https://n8n.optic.works
- Login with credentials from `.env`

## Workflows

### Hourly X Poster (Simple)
Automated hourly tweets for OpticWorks brand awareness.

- **Trigger:** Cron (every hour at :00)
- **Action:** Posts tweet via Tweet API shim
- **Content:** Rotating marketing messages (8 variants)

Uses the Tweet API shim service to handle OAuth signing. See [Tweet API Shim docs](docs/tweet-api-shim.md).

## Tweet API Shim

A lightweight Python service that handles X OAuth 1.0a signing, bypassing N8N's credential system.

- **Location:** `/opt/n8n/tweet-api.py`
- **Port:** 5680 (localhost only)
- **Service:** `tweet-api.service`

```bash
# Check status
ssh n100 "sudo systemctl status tweet-api"

# Test manually
ssh n100 'curl -X POST http://127.0.0.1:5680 -H "Content-Type: application/json" -d "{\"text\": \"Test tweet\"}"'
```

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `N8N_ENCRYPTION_KEY` | Encrypts stored credentials |
| `N8N_AUTH_USER` | Basic auth username |
| `N8N_AUTH_PASSWORD` | Basic auth password |
| `X_API_KEY` | X API key |
| `X_API_SECRET` | X API secret |
| `X_ACCESS_TOKEN` | X access token |
| `X_ACCESS_SECRET` | X access token secret |

## Documentation

- [**SETUP.md**](SETUP.md) - Complete step-by-step deployment guide
- [X API Setup Guide](docs/x-api-setup.md) - Create X Developer account and get credentials
- [Cloudflare Setup Guide](docs/cloudflare-setup.md) - Configure tunnel for n8n.optic.works
- [Tweet API Shim](docs/tweet-api-shim.md) - OAuth shim service documentation

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/tweet-api.py` | OAuth shim service for X API |
| `scripts/tweet-api.service` | Systemd unit file |
| `scripts/backup-workflows.sh` | Export workflows from N8N |

## Maintenance

### Backup Workflows
```bash
./scripts/backup-workflows.sh
```

### Update N8N
```bash
ssh n100
cd /opt/n8n
docker compose pull
docker compose up -d
```

## License

Private - OpticWorks
