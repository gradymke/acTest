from flask import Flask, render_template, request
import boto3
import json
import os

app = Flask(__name__)

APP_CONFIG_APP = os.environ.get('APP_CONFIG_APP', 'acTestApplication')
APP_CONFIG_CONFIG = os.environ.get('APP_CONFIG_CONFIG', 'acTest')
AWS_REGION = os.environ.get('AWS_REGION', 'us-west-2')


def get_app_config(env):
    client = boto3.client('appconfigdata', region_name=AWS_REGION)

    session_response = client.start_configuration_session(
        ApplicationIdentifier=APP_CONFIG_APP,
        EnvironmentIdentifier=env,
        ConfigurationProfileIdentifier=APP_CONFIG_CONFIG
    )

    token = session_response['InitialConfigurationToken']

    response = client.get_latest_configuration(ConfigurationToken=token)
    config_content = response['Configuration']

    if hasattr(config_content, 'read'):
        config_content = config_content.read().decode('utf-8')

    return json.loads(config_content)


@app.route('/')
def index():
    env = request.args.get('env', 'dev')
    
    try:
        config = get_app_config(env)
    except Exception as e:
        config = {'feature1': 'false', 'feature2': 'false'}
        print(f"Error fetching config: {e}")

    return render_template(
        'index.html',
        feature1=config.get('feature1', 'false'),
        feature2=config.get('feature2', 'false'),
        env=env
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
