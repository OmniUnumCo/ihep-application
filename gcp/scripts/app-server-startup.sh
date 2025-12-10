#!/bin/bash

# Application Server Startup Script for Health Insight Ventures
set -e

# Update system
apt-get update
apt-get install -y nodejs npm git curl postgresql-client

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Create application user
useradd -m -s /bin/bash healthapp
mkdir -p /opt/health-insight
chown healthapp:healthapp /opt/health-insight

# Clone and setup application
cd /opt/health-insight
sudo -u healthapp git clone https://github.com/your-repo/health-insight-ventures.git .

# Install dependencies
sudo -u healthapp npm ci --only=production

# Create environment file
cat > /opt/health-insight/.env << 'EOF'
NODE_ENV=production
PORT=3000
DATABASE_URL=postgresql://healthapp:password@10.3.1.10:5432/health_insight_db
DATABASE_REPLICA_URL=postgresql://healthapp:password@10.3.2.10:5432/health_insight_db
REDIS_URL=redis://10.3.1.20:6379
LOG_LEVEL=info
MAX_CONNECTIONS=20
EOF

chown healthapp:healthapp /opt/health-insight/.env
chmod 600 /opt/health-insight/.env

# Build application
sudo -u healthapp npm run build

# Create systemd service
cat > /etc/systemd/system/health-insight.service << 'EOF'
[Unit]
Description=Health Insight Ventures Application
After=network.target

[Service]
Type=simple
User=healthapp
WorkingDirectory=/opt/health-insight
Environment=NODE_ENV=production
EnvironmentFile=/opt/health-insight/.env
ExecStart=/usr/bin/node dist/index.js
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=health-insight
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

# Create health check endpoint script
cat > /opt/health-insight/health-check.js << 'EOF'
const http = require('http');

const healthServer = http.createServer((req, res) => {
  if (req.url === '/api/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime()
    }));
  } else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

healthServer.listen(3001, () => {
  console.log('Health check server listening on port 3001');
});
EOF

chown healthapp:healthapp /opt/health-insight/health-check.js

# Create health check service
cat > /etc/systemd/system/health-check.service << 'EOF'
[Unit]
Description=Health Check Service
After=network.target

[Service]
Type=simple
User=healthapp
WorkingDirectory=/opt/health-insight
ExecStart=/usr/bin/node health-check.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Setup log rotation
cat > /etc/logrotate.d/health-insight << 'EOF'
/var/log/syslog {
    daily
    missingok
    rotate 30
    compress
    notifempty
    sharedscripts
    postrotate
        systemctl reload rsyslog
    endscript
}
EOF

# Setup monitoring agent
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
bash add-google-cloud-ops-agent-repo.sh --also-install

# Configure custom metrics
cat > /etc/google-cloud-ops-agent/config.yaml << 'EOF'
metrics:
  receivers:
    nodejs:
      type: nodejs
      collection_interval: 60s
  processors:
    batch:
      timeout: 10s
  exporters:
    google_cloud_monitoring:
      type: google_cloud_monitoring
  service:
    pipelines:
      default_pipeline:
        receivers: [nodejs]
        processors: [batch]
        exporters: [google_cloud_monitoring]

logging:
  receivers:
    syslog:
      type: files
      include_paths:
        - /var/log/syslog
      exclude_paths:
        - /var/log/syslog.1
  processors:
    batch:
      timeout: 10s
  exporters:
    google_cloud_logging:
      type: google_cloud_logging
  service:
    pipelines:
      default_pipeline:
        receivers: [syslog]
        processors: [batch]
        exporters: [google_cloud_logging]
EOF

# Enable and start services
systemctl daemon-reload
systemctl enable health-insight
systemctl enable health-check
systemctl enable google-cloud-ops-agent

systemctl start health-check
systemctl start health-insight
systemctl start google-cloud-ops-agent

# Wait for application to start
sleep 30

# Verify services are running
systemctl status health-insight
systemctl status health-check

echo "Application server setup completed successfully"