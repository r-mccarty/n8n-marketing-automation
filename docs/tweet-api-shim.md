# Tweet API Shim Service

A lightweight Python HTTP service that handles X (Twitter) OAuth 1.0a signing, bypassing N8N's credential system which has compatibility issues with X's API.

## Architecture

```
N8N Workflow → HTTP POST → Tweet API (port 5680) → X API v2
                          (handles OAuth signing)
```

## Why This Exists

N8N's built-in X/Twitter credential system has issues with OAuth flows. This shim:
- Runs locally on N100 (port 5680, localhost only)
- Handles OAuth 1.0a signing using `requests-oauthlib`
- Exposes a simple JSON API for N8N to call
- Credentials are stored in the Python script (or can be env vars)

## Installation

The shim is installed at `/opt/n8n/tweet-api.py` and runs as a systemd service.

### Files

| Path | Purpose |
|------|---------|
| `/opt/n8n/tweet-api.py` | Python HTTP server |
| `/etc/systemd/system/tweet-api.service` | Systemd unit |
| `/opt/n8n/tweet-api.log` | Logs (if running manually) |

### Dependencies

```bash
sudo pip3 install requests requests-oauthlib --break-system-packages
```

### Service Management

```bash
# Status
sudo systemctl status tweet-api

# Restart
sudo systemctl restart tweet-api

# Logs
sudo journalctl -u tweet-api -f
```

## API Usage

### POST /

Post a tweet.

**Request:**
```bash
curl -X POST http://127.0.0.1:5680 \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from the API!"}'
```

**Response (201):**
```json
{
  "data": {
    "id": "1234567890",
    "text": "Hello from the API!"
  }
}
```

## N8N Workflow

The **"Hourly X Poster (Simple)"** workflow uses this API:

1. **Every Hour** - Schedule trigger
2. **Pick Message** - Code node rotates through marketing messages
3. **Post Tweet** - HTTP Request to `http://127.0.0.1:5680`

No N8N credentials needed - the shim handles all authentication.

## Updating Credentials

Edit `/opt/n8n/tweet-api.py` and update the credential variables:

```python
API_KEY = "your-api-key"
API_SECRET = "your-api-secret"
ACCESS_TOKEN = "your-access-token"
ACCESS_SECRET = "your-access-secret"
```

Then restart: `sudo systemctl restart tweet-api`

## Security Notes

- Service only listens on `127.0.0.1` (not exposed externally)
- Credentials are stored in plain text in the Python script
- Consider using environment variables for production:

```python
import os
API_KEY = os.environ.get("X_API_KEY")
# etc.
```
