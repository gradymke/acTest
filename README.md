# Feature Flag Demo

A simple Flask application demonstrating feature flags using AWS AppConfig and Unleash providers.

## Prerequisites

- Python 3.11+
- For AppConfig: AWS credentials configured (via environment variables, ~/.aws/credentials, or IAM role)
- For Unleash: Sign up at [Unleash](https://getunleash.io) and create API keys

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

Update your AppConfig configuration in AWS Console:
```json
{
  "feature1": "true",
  "feature2": "true"
}
```

Refresh the page to see changes (new configuration is fetched on each request).

## Unleash Provider Setup

To use the Unleash provider:

1. Sign up at [Unleash](https://getunleash.io)
2. Create an API token for each environment (dev, test, prod)
3. Update the `UNLEASH_API_KEYS` dictionary in `app.py` with your keys:

```python
UNLEASH_API_KEYS = {
    "dev": "your-dev-api-key",
    "test": "your-test-api-key",
    "prod": "your-prod-api-key",
}
```

4. Select "Unleash" from the provider dropdown in the UI


# Unleash

Unleash is another "open source" solution for feature flags. I opted to try out their cloud trial version, however, since it's easier to get up and running more quickly.

https://www.getunleash.io/

## Notes

Signed up for a free trial account. Cool feature, when you do something in the UI, it gives you the equivalent CURL command on the same window so you can script it!

project: ulTest

Created a flag, `feature1`. Interesting, when you create a flag, you can use one of several "types" of flags:
* Release
* Experiment
* Operational
* Kill switch
* Permission
It looks like this is for informational purposes only, all flags have the same capabilities.

You can tag a flag - that's nice. I think you can do that in AppConfig as well.

Impression data helps you track to see how your flag is being used? This might be interesting - not sure of a comparable feaure in AppConfig.

Created environments - environments have "environment types" to help with visibility, I would imagine? Environment types include:
* Development
* Test
* Pre Production
* Production

Sort order also seems to be important in this tool as you can drag your environments up and down in the env list.

Strategies are deployment models. You can define the default strategy on a per-environment basis, which is REALLY NICE!!!

Has 2 default strategies - Standard, which just rolls everything out, and Gradual, which gives you options for how it gradually rolls it out (based on userId, sessionID, random, etc)

You can create custom strategies, but it wasn't obvious how that worked, so I stopped looking at it.

There is also something called `Release Templates` which rolls things out to percentages of users.

When configuring things on environments, it warns you if you change something on a Production environment - that's kind of nice.

API Keys are generated per environment - interesting...

Pricing - $75 per seat per month. So if we had 10 seats, that's $9,000 per year. Not sure what our seat strategy should be... If we self host, we have to determine what it costs to maintain.
