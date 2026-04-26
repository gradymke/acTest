# AWS AppConfig Demo

A simple Flask application demonstrating AWS AppConfig feature flags.

## Prerequisites

- Python 3.8+
- AWS credentials configured (via environment variables, ~/.aws/credentials, or IAM role)
- IAM permissions to access AppConfig Data API

## Required IAM Permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "appconfig:StartConfigurationSession",
                "appconfig:GetConfiguration"
            ],
            "Resource": "arn:aws:appconfig:*:your-account:application/demo-app/environment/demo-env/configuration/demo-config"
        }
    ]
}
```

## Setup

1. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

2. Set environment variables (or rely on default credentials):
   ```bash
   export APP_CONFIG_APP=demo-app
   export APP_CONFIG_ENV=demo-env
   export APP_CONFIG_CONFIG=demo-config
   export AWS_REGION=us-east-1
   ```

3. Run the app:
   ```bash
   uv run app.py
   ```

4. Open http://localhost:8000 in your browser

## Changing Feature Flags

Update your AppConfig configuration in AWS Console:
```json
{
  "feature1": "true",
  "feature2": "true"
}
```

Refresh the page to see changes (new configuration is fetched on each request).
