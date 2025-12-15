def GenerateConfig(context):
    """Generate the monitoring configuration."""
    
    project = context.properties['project']
    notification_email = context.properties['notificationEmail']
    
    resources = []
    
    # Notification channel
    resources.append({
        'name': 'health-insight-notification-channel',
        'type': 'monitoring.v1.notificationChannel',
        'properties': {
            'type': 'email',
            'displayName': 'Health Insight Admin Email',
            'labels': {
                'email_address': notification_email
            }
        }
    })
    
    # Alert policies
    alert_policies = [
        {
            'name': 'high-cpu-usage',
            'displayName': 'High CPU Usage',
            'conditions': [{
                'displayName': 'CPU usage above 80%',
                'conditionThreshold': {
                    'filter': 'resource.type="gce_instance"',
                    'comparison': 'COMPARISON_GT',
                    'thresholdValue': 0.8,
                    'duration': '300s'
                }
            }]
        },
        {
            'name': 'instance-down',
            'displayName': 'Instance Down',
            'conditions': [{
                'displayName': 'Instance not responding',
                'conditionAbsent': {
                    'filter': 'resource.type="gce_instance"',
                    'duration': '300s'
                }
            }]
        }
    ]
    
    for policy in alert_policies:
        resources.append({
            'name': f"health-insight-{policy['name']}",
            'type': 'monitoring.v1.alertPolicy',
            'properties': {
                'displayName': policy['displayName'],
                'conditions': policy['conditions'],
                'notificationChannels': [
                    f'$(ref.health-insight-notification-channel.name)'
                ],
                'enabled': True
            }
        })
    
    return {'resources': resources}