#!/usr/bin/env bash

# Simple API verification script for staging/local Mayan EDMS
# Usage:
#   export TOKEN="your-token-here"
#   export DOC_ID="123"   # optional, for new_from_edit smoke
#   ./verify_api.sh

set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8080/api/v4}"
TOKEN_HEADER=()
if [[ -n "${TOKEN:-}" ]]; then
  TOKEN_HEADER=(-H "Authorization: Token ${TOKEN}")
else
  echo "[WARN] TOKEN not set; authenticated endpoints will return 401"
fi

echo "== Ping current user =="
curl -i "${TOKEN_HEADER[@]}" \
  -H "Accept: application/json" \
  "${BASE_URL}/users/current/" || true

echo -e "\n== List documents (optimized) =="
curl -i "${TOKEN_HEADER[@]}" \
  -H "Accept: application/json" \
  "${BASE_URL}/documents/optimized/" || true

if [[ -n "${DOC_ID:-}" ]]; then
  echo -e "\n== Smoke: new_from_edit (HEADLESS) =="
  # This is a metadata-only probe; server will reject without file, but proves route exists
  curl -i "${TOKEN_HEADER[@]}" \
    -X POST \
    -H "Accept: application/json" \
    "${BASE_URL}/headless/documents/${DOC_ID}/versions/new_from_edit/" || true
else
  echo "[INFO] DOC_ID not set; skipping new_from_edit probe"
fi

echo -e "\nDone."

