#!/bin/sh
# Generates a self-signed cert/key for local HTTPS testing.
# Valid for localhost + 127.0.0.1, 365 days.
set -e
cd "$(dirname "$0")"

openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout key.pem -out cert.pem -days 365 \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

echo "Wrote backend/certs/cert.pem and backend/certs/key.pem"
