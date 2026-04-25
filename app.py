from flask import Flask, render_template
import boto3
import json
import os

app = Flask(__name__)

APP_CONFIG_APP = os.environ.get('APP_CONFIG_APP', 'demo-app')
APP_CONFIG_ENV = os.environ.get('APP_CONFIG_ENV', 'demo-env')
APP_CONFIG_CONFIG = os.environ.get('APP_CONFIG_CONFIG', 'demo-config')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')


def get_app_config():
    client = boto3.client('appconfigdata', region_name=AWS_REGION)
    
    config_session = client.start_configuration_session(
        ApplicationIdentifier=APP_CONFIG_APP,
        EnvironmentIdentifier=APP_CONFIG_ENV,
        ConfigurationIdentifier=APP_CONFIG_CONFIG
    )
    
    response = client.get_configuration(Configuration=config_session)
    config_content = response['Configuration']
    
    if isinstance(config_content, bytes):
        config_content = config_content.decode('utf-8')
    
    return json.loads(config_content)


@app.route('/')
def index():
    try:
        config = get_app_config()
    except Exception as e:
        config = {'feature1': 'false', 'feature2': 'false'}
        print(f"Error fetching config: {e}")
    
    return render_template(
        'index.html',
        feature1=config.get('feature1', 'false'),
        feature2=config.get('feature2', 'false')
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)