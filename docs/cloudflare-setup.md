# Cloudflare Tunnel Setup for N8N

This guide covers configuring Cloudflare tunnel to expose N8N at `n8n.optic.works`.

## Prerequisites

- Cloudflare account with `optic.works` domain
- Cloudflared installed on N100
- Existing tunnel configured (used for other services)

---

## Step 1: Verify Existing Tunnel

```bash
ssh n100

# Check cloudflared status
sudo systemctl status cloudflared

# View current config
sudo cat /etc/cloudflared/config.yml
```

---

## Step 2: Add N8N Ingress Rule

Edit the cloudflared configuration:

```bash
sudo nano /etc/cloudflared/config.yml
```

Add the N8N ingress rule:

```yaml
tunnel: <your-tunnel-id>
credentials-file: /etc/cloudflared/<tunnel-id>.json

ingress:
  # Existing rules...
  - hostname: coder.hardwareos.com
    service: http://localhost:7080
  - hostname: ha.hardwareos.com
    service: http://localhost:8123

  # Add N8N
  - hostname: n8n.optic.works
    service: http://localhost:5678

  # Catch-all (must be last)
  - service: http_status:404
```

---

## Step 3: Add DNS Record

### Option A: Via Cloudflare Dashboard

1. Go to Cloudflare Dashboard → `optic.works` → DNS
2. Add record:
   - Type: `CNAME`
   - Name: `n8n`
   - Target: `<tunnel-id>.cfargotunnel.com`
   - Proxy: ON (orange cloud)

### Option B: Via Cloudflare API

```bash
# Using CLOUDFLARE_API_TOKEN from Infisical
curl -X POST "https://api.cloudflare.com/client/v4/zones/<zone-id>/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "CNAME",
    "name": "n8n",
    "content": "<tunnel-id>.cfargotunnel.com",
    "proxied": true
  }'
```

---

## Step 4: Restart Cloudflared

```bash
sudo systemctl restart cloudflared

# Verify it's running
sudo systemctl status cloudflared

# Check logs for errors
sudo journalctl -u cloudflared -f
```

---

## Step 5: Verify Access

```bash
# Test from anywhere
curl -I https://n8n.optic.works

# Should return 401 (N8N basic auth) or 200 if not configured
```

Open in browser: https://n8n.optic.works

---

## Security Notes

1. **Basic Auth:** N8N is protected with basic auth (configured in docker-compose)
2. **HTTPS:** All traffic is encrypted via Cloudflare
3. **Access Control:** Consider adding Cloudflare Access for additional protection

### Optional: Add Cloudflare Access

For extra security, add Cloudflare Access in front of N8N:

1. Go to Cloudflare Zero Trust → Access → Applications
2. Add application for `n8n.optic.works`
3. Configure authentication (email, OAuth, etc.)

---

## Troubleshooting

### "Bad Gateway" Error
- Ensure N8N is running: `docker ps | grep n8n`
- Check N8N logs: `docker logs n8n`
- Verify port 5678 is listening: `ss -tlnp | grep 5678`

### "Tunnel Connection Failed"
- Check cloudflared logs: `sudo journalctl -u cloudflared`
- Verify tunnel credentials file exists
- Restart cloudflared: `sudo systemctl restart cloudflared`

### DNS Not Resolving
- Wait 5 minutes for propagation
- Check DNS record in Cloudflare dashboard
- Verify CNAME target is correct
