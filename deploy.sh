#!/bin/bash
# =============================================================
# Deploy script for La Bible de l'IA on Hostinger VPS
#
# FIRST TIME SETUP:
#   1. SSH into your VPS: ssh root@YOUR_VPS_IP
#   2. Install Nginx + PHP:
#      apt update && apt install -y nginx php-fpm php-cli git
#   3. Create web directory:
#      mkdir -p /var/www/labibledelia.com
#   4. Clone the repo:
#      cd /var/www && git clone https://github.com/gazuloic-oss/labibledelia.git labibledelia.com
#   5. Copy Nginx config:
#      cp /var/www/labibledelia.com/nginx.conf /etc/nginx/sites-available/labibledelia.com
#      ln -s /etc/nginx/sites-available/labibledelia.com /etc/nginx/sites-enabled/
#      rm -f /etc/nginx/sites-enabled/default
#   6. Test & reload Nginx:
#      nginx -t && systemctl reload nginx
#   7. Setup SSL (if not already done by Hostinger):
#      apt install -y certbot python3-certbot-nginx
#      certbot --nginx -d labibledelia.com -d www.labibledelia.com
#   8. Configure PHP-FPM socket (check with: ls /var/run/php/php*-fpm.sock)
#      If your socket path differs, update nginx.conf fastcgi_pass line
#
# SUBSEQUENT DEPLOYS (run this script):
#   ssh root@YOUR_VPS_IP 'bash -s' < deploy.sh
#   OR run directly on the VPS
# =============================================================

set -e

SITE_DIR="/var/www/labibledelia.com"

echo "🔄 Deploying La Bible de l'IA..."

# Pull latest changes
cd "$SITE_DIR"
git pull origin main

# Set correct permissions
chown -R www-data:www-data "$SITE_DIR"
chmod -R 755 "$SITE_DIR"
chmod 644 "$SITE_DIR/api/submit.php"

# Test Nginx config
nginx -t

# Reload Nginx (graceful, no downtime)
systemctl reload nginx

echo "✅ Deploy complete! Site is live at https://labibledelia.com"
