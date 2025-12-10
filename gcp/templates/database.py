def GenerateConfig(context):
    """Generate the database configuration."""
    
    project = context.properties['project']
    region = context.properties['region']
    instance_name = context.properties['instanceName']
    database_version = context.properties['databaseVersion']
    tier = context.properties['tier']
    
    resources = []
    
    # Cloud SQL instance
    resources.append({
        'name': instance_name,
        'type': 'sqladmin.v1beta4.instance',
        'properties': {
            'region': region,
            'databaseVersion': database_version,
            'settings': {
                'tier': tier,
                'backupConfiguration': {
                    'enabled': True,
                    'startTime': '03:00'
                },
                'ipConfiguration': {
                    'ipv4Enabled': True,
                    'authorizedNetworks': []
                },
                'locationPreference': {
                    'zone': f'{region}-a'
                }
            }
        }
    })
    
    # Database
    resources.append({
        'name': 'health-insight-db',
        'type': 'sqladmin.v1beta4.database',
        'properties': {
            'name': 'health_insight',
            'instance': f'$(ref.{instance_name}.name)',
            'charset': 'UTF8'
        }
    })
    
    # Database user
    resources.append({
        'name': 'health-insight-user',
        'type': 'sqladmin.v1beta4.user',
        'properties': {
            'name': 'app_user',
            'instance': f'$(ref.{instance_name}.name)',
            'password': 'change-this-password'  # Use Secret Manager in production
        }
    })
    
    return {'resources': resources}