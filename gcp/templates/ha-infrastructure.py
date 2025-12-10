def GenerateConfig(context):
    """Generate the HA infrastructure configuration."""
    
    project = context.properties['project']
    region = context.properties['region']
    zones = context.properties['zones']
    domain = context.properties['domain']
    
    resources = []
    
    # VPC Network
    resources.append({
        'name': 'health-insight-vpc',
        'type': 'compute.v1.network',
        'properties': {
            'autoCreateSubnetworks': False,
            'description': 'Health Insight Ventures VPC network'
        }
    })
    
    # Subnets for each zone
    for i, zone in enumerate(zones):
        resources.append({
            'name': f'health-insight-subnet-{i+1}',
            'type': 'compute.v1.subnetwork',
            'properties': {
                'network': f'$(ref.health-insight-vpc.selfLink)',
                'ipCidrRange': f'10.{i+1}.0.0/24',
                'region': region,
                'description': f'Subnet for zone {zone}'
            }
        })
    
    # Firewall rules
    firewall_rules = [
        {
            'name': 'allow-health-check',
            'allowed': [{'IPProtocol': 'tcp', 'ports': ['80', '443', '8080']}],
            'sourceRanges': ['130.211.0.0/22', '35.191.0.0/16'],
            'targetTags': ['health-check']
        },
        {
            'name': 'allow-web-traffic',
            'allowed': [{'IPProtocol': 'tcp', 'ports': ['80', '443']}],
            'sourceRanges': ['0.0.0.0/0'],
            'targetTags': ['web-server']
        },
        {
            'name': 'allow-internal',
            'allowed': [{'IPProtocol': 'tcp', 'ports': ['0-65535']}],
            'sourceRanges': ['10.0.0.0/8'],
            'targetTags': ['internal']
        }
    ]
    
    for rule in firewall_rules:
        resources.append({
            'name': f"health-insight-{rule['name']}",
            'type': 'compute.v1.firewall',
            'properties': {
                'network': f'$(ref.health-insight-vpc.selfLink)',
                **rule
            }
        })
    
    # Instance templates
    web_template = {
        'name': 'health-insight-web-template',
        'type': 'compute.v1.instanceTemplate',
        'properties': {
            'properties': {
                'machineType': 'e2-medium',
                'disks': [{
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': 'projects/ubuntu-os-cloud/global/images/family/ubuntu-2004-lts'
                    }
                }],
                'networkInterfaces': [{
                    'network': f'$(ref.health-insight-vpc.selfLink)',
                    'subnetwork': f'$(ref.health-insight-subnet-1.selfLink)',
                    'accessConfigs': [{'type': 'ONE_TO_ONE_NAT'}]
                }],
                'tags': {
                    'items': ['web-server', 'health-check']
                },
                'metadata': {
                    'items': [{
                        'key': 'startup-script',
                        'value': '''#!/bin/bash
apt-get update
apt-get install -y nginx nodejs npm git
systemctl enable nginx
systemctl start nginx

# Clone application code (replace with your repo)
cd /opt
git clone https://github.com/your-repo/health-insight-app.git
cd health-insight-app

# Install dependencies and start
npm install
npm run build
npm run start &

# Configure nginx proxy
cat > /etc/nginx/sites-available/default << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
}
EOF

systemctl reload nginx
'''
                    }]
                }
            }
        }
    }
    
    app_template = {
        'name': 'health-insight-app-template',
        'type': 'compute.v1.instanceTemplate',
        'properties': {
            'properties': {
                'machineType': 'e2-standard-2',
                'disks': [{
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': 'projects/ubuntu-os-cloud/global/images/family/ubuntu-2004-lts'
                    }
                }],
                'networkInterfaces': [{
                    'network': f'$(ref.health-insight-vpc.selfLink)',
                    'subnetwork': f'$(ref.health-insight-subnet-1.selfLink)'
                }],
                'tags': {
                    'items': ['app-server', 'health-check', 'internal']
                },
                'metadata': {
                    'items': [{
                        'key': 'startup-script',
                        'value': '''#!/bin/bash
apt-get update
apt-get install -y nodejs npm git postgresql-client

# Clone and setup application
cd /opt
git clone https://github.com/your-repo/health-insight-app.git
cd health-insight-app

npm install
npm run build

# Start application server
PORT=8080 npm run start:server &

# Health check endpoint
echo "App server started on port 8080"
'''
                    }]
                }
            }
        }
    }
    
    resources.extend([web_template, app_template])
    
    # Instance groups
    for i, zone in enumerate(zones):
        # Web server group
        resources.append({
            'name': f'health-insight-web-group-{i+1}',
            'type': 'compute.v1.instanceGroupManager',
            'properties': {
                'zone': zone,
                'instanceTemplate': f'$(ref.health-insight-web-template.selfLink)',
                'targetSize': 2,
                'baseInstanceName': f'web-server-{i+1}'
            }
        })
        
        # App server group
        resources.append({
            'name': f'health-insight-app-group-{i+1}',
            'type': 'compute.v1.instanceGroupManager',
            'properties': {
                'zone': zone,
                'instanceTemplate': f'$(ref.health-insight-app-template.selfLink)',
                'targetSize': 3,
                'baseInstanceName': f'app-server-{i+1}'
            }
        })
    
    # Health checks
    resources.extend([
        {
            'name': 'health-insight-web-health-check',
            'type': 'compute.v1.httpHealthCheck',
            'properties': {
                'requestPath': '/health',
                'port': 80,
                'checkIntervalSec': 30,
                'timeoutSec': 5
            }
        },
        {
            'name': 'health-insight-app-health-check',
            'type': 'compute.v1.httpHealthCheck',
            'properties': {
                'requestPath': '/api/health',
                'port': 8080,
                'checkIntervalSec': 30,
                'timeoutSec': 5
            }
        }
    ])
    
    # Backend services
    resources.extend([
        {
            'name': 'health-insight-web-backend',
            'type': 'compute.v1.backendService',
            'properties': {
                'healthChecks': [f'$(ref.health-insight-web-health-check.selfLink)'],
                'backends': [
                    {
                        'group': f'$(ref.health-insight-web-group-1.instanceGroup)',
                        'balancingMode': 'UTILIZATION'
                    },
                    {
                        'group': f'$(ref.health-insight-web-group-2.instanceGroup)',
                        'balancingMode': 'UTILIZATION'
                    }
                ],
                'protocol': 'HTTP',
                'port': 80
            }
        }
    ])
    
    # URL Map
    resources.append({
        'name': 'health-insight-url-map',
        'type': 'compute.v1.urlMap',
        'properties': {
            'defaultService': f'$(ref.health-insight-web-backend.selfLink)'
        }
    })
    
    # HTTP Proxy
    resources.append({
        'name': 'health-insight-http-proxy',
        'type': 'compute.v1.targetHttpProxy',
        'properties': {
            'urlMap': f'$(ref.health-insight-url-map.selfLink)'
        }
    })
    
    # Global forwarding rule
    resources.append({
        'name': 'health-insight-forwarding-rule',
        'type': 'compute.v1.globalForwardingRule',
        'properties': {
            'target': f'$(ref.health-insight-http-proxy.selfLink)',
            'portRange': '80'
        }
    })
    
    return {'resources': resources}