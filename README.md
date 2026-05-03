# Feature Flag Demo

A simple Flask application demonstrating feature flags using OpenFeature SDK with AWS AppConfig and Unleash providers.

## Prerequisites

- Python 3.11+
- For AppConfig: AWS credentials configured (via environment variables, ~/.aws/credentials, or IAM role)
- For Unleash: Sign up at [Unleash](https://getunleash.io) and create API keys

## Required IAM Permissions (for AppConfig)

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

## Connect to AWS

```bash
aws login
```

## Setup

1. Install dependencies:
   ```bash
   uv sync
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

### AppConfig
Update your AppConfig configuration in AWS Console:
```json
{
  "feature1": {"enabled": true},
  "feature2": {"enabled": true}
}
```

Refresh the page to see changes (new configuration is fetched on each request).

### Unleash
Configure flags in your Unleash console at https://getunleash.io

## Unleash Provider Setup

To use the Unleash provider:

1. Sign up at [Unleash](https://getunleash.io)
2. Create an API token for each environment (dev, test, prod)
3. Update the `UNLEASH_API_KEYS` dictionary in `app.py` with your keys

4. Select "Unleash" from the provider dropdown in the UI

## OpenFeature

This application uses the [OpenFeature](https://openfeature.dev) SDK to provide a vendor-neutral feature flag evaluation interface.

- Unleash backend uses the official `openfeature-provider-unleash`
- AppConfig backend uses a custom `AwsAppConfigProvider` implementing the OpenFeature `AbstractProvider` interface

## Notes

The OpenFeature SDK allows easy switching between feature flag backends without code changes to the flag evaluation logic.
