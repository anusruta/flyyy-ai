#!/bin/bash
# FLYYY.AI Production Deploy Script
# Usage: bash scripts/deploy.sh yourdomain.com

set -e

DOMAIN=${1:?"Usage: bash deploy.sh yourdomain.com"}
EMAIL=${2:?"Usage: bash deploy.sh yourdomain.com admin@yourdomain.com"}

echo "🚀 Deploying FLYYY.AI to $DOMAIN"

# 1. Replace domain placeholder in nginx config
sed -i "s/YOUR_DOMAIN_HERE/$DOMAIN/g" nginx.prod.conf

# 2. Create certbot dirs
mkdir -p certbot/conf certbot/www

# 3. Obtain SSL certificate (first run: standalone mode)
echo "📜 Obtaining SSL certificate for $DOMAIN..."
docker run --rm -p 80:80 \
  -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
  -v "$(pwd)/certbot/www:/var/www/certbot" \
  certbot/certbot certonly \
  --standalone \
  --email $EMAIL \
  --agree-tos \
  --no-eff-email \
  -d $DOMAIN -d www.$DOMAIN

# 4. Build and start all services
echo "🐳 Building Docker images..."
docker compose -f docker-compose.prod.yml --env-file .env.production build --no-cache

echo "▶️  Starting all services..."
docker compose -f docker-compose.prod.yml --env-file .env.production up -d

echo ""
echo "✅ FLYYY.AI is live at https://$DOMAIN"
echo "   Dashboard  → https://$DOMAIN"
echo "   API Docs   → https://$DOMAIN/docs"
