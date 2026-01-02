#!/bin/bash
# Backup N8N workflows to the workflows/ directory

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
WORKFLOWS_DIR="$REPO_DIR/workflows"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)

# N8N API endpoint (update if using different host)
N8N_HOST="${N8N_HOST:-https://n8n.optic.works}"
N8N_API_KEY="${N8N_API_KEY:-}"

echo "Backing up N8N workflows from $N8N_HOST"

# Create workflows directory if it doesn't exist
mkdir -p "$WORKFLOWS_DIR"

# If API key is set, use API to export
if [ -n "$N8N_API_KEY" ]; then
    echo "Using N8N API to export workflows..."

    # Get all workflows
    curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
        "$N8N_HOST/api/v1/workflows" | \
        jq -r '.data[] | @base64' | while read workflow; do

        # Decode and extract workflow details
        _jq() {
            echo "$workflow" | base64 -d | jq -r "${1}"
        }

        name=$(_jq '.name')
        id=$(_jq '.id')

        # Sanitize filename
        filename=$(echo "$name" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]-_')

        echo "Exporting: $name ($id)"

        # Export workflow
        curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
            "$N8N_HOST/api/v1/workflows/$id" \
            -o "$WORKFLOWS_DIR/${filename}.json"
    done
else
    echo "No N8N_API_KEY set. Manual export required:"
    echo "1. Open N8N at $N8N_HOST"
    echo "2. Go to each workflow"
    echo "3. Click '...' menu → 'Download'"
    echo "4. Save to $WORKFLOWS_DIR/"
fi

echo ""
echo "Backup complete! Workflows saved to: $WORKFLOWS_DIR/"
ls -la "$WORKFLOWS_DIR/"
