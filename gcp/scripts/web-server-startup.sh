#!/bin/bash

# Web Server Startup Script for Health Insight Ventures
set -e

# Update system
apt-get update
apt-get install -y nginx nodejs npm git curl

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Create application directory
mkdir -p /opt/health-insight
cd /opt/health-insight

# Configure Nginx as reverse proxy
cat > /etc/nginx/sites-available/health-insight << 'EOF'
upstream app_servers {
    server 10.2.1.10:3000;
    server 10.2.1.11:3000;
    server 10.2.2.10:3000;
    server 10.2.2.11:3000;
}

server {
    listen 80;
    listen [::]:80;
    server_name ihep.app www.ihep.app api.ihep.app;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ihep.app www.ihep.app;
    
    ssl_certificate /etc/ssl/certs/ihep_app.crt;
    ssl_certificate_key /etc/ssl/private/ihep_app.key;
    
    location / {
        proxy_pass http://app_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    location /static/ {
        alias /opt/health-insight/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.ihep.app;
    
    ssl_certificate /etc/ssl/certs/ihep_app.crt;
    ssl_certificate_key /etc/ssl/private/ihep_app.key;
    
    location / {
        proxy_pass http://app_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/health-insight /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and start Nginx
nginx -t
systemctl enable nginx
systemctl start nginx

# Configure log rotation
cat > /etc/logrotate.d/health-insight << 'EOF'
/var/log/nginx/access.log
/var/log/nginx/error.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 0644 www-data www-data
    sharedscripts
    postrotate
        if [ -f /var/run/nginx.pid ]; then
            kill -USR1 `cat /var/run/nginx.pid`
        fi
    endscript
}
EOF

# Setup monitoring agent
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
bash add-google-cloud-ops-agent-repo.sh --also-install

# Configure health check endpoint
systemctl enable nginx
systemctl restart nginx

echo "Web server setup completed successfully"