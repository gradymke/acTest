# AWS AppConfig Demo - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Flask web app that fetches feature flags from AWS AppConfig and displays UI sections conditionally.

**Architecture:** Single Flask app uses boto3 to call AppConfig Data API, renders Jinja2 template with feature flags as template variables.

**Tech Stack:** Python, Flask, boto3, Jinja2

---

### Task 1: Create requirements.txt

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: Write requirements.txt**

```
Flask>=2.0.0
boto3>=1.26.0
```

- [ ] **Step 2: Commit**

```bash
git add requirements.txt
git commit -m "chore: add Flask and boto3 dependencies"
```

---

### Task 2: Create Flask app with AppConfig integration

**Files:**
- Create: `app.py`

- [ ] **Step 1: Write app.py**

```python
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
    
    # Start configuration session
    config_session = client.start_configuration_session(
        ApplicationIdentifier=APP_CONFIG_APP,
        EnvironmentIdentifier=APP_CONFIG_ENV,
        ConfigurationIdentifier=APP_CONFIG_CONFIG
    )
    
    # Get configuration
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
```

- [ ] **Step 2: Commit**

```bash
git add app.py
git commit -m "feat: add Flask app with AppConfig integration"
```

---

### Task 3: Create HTML template

**Files:**
- Create: `templates/index.html`

- [ ] **Step 1: Create templates directory**

```bash
mkdir -p templates
```

- [ ] **Step 2: Write templates/index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS AppConfig Demo</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        .feature {
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
        }
        .feature-feature1 {
            background: #d4edda;
            border: 2px solid #28a745;
        }
        .feature-feature2 {
            background: #d1ecf1;
            border: 2px solid #17a2b8;
        }
        .feature h2 {
            margin-top: 0;
        }
        .disabled {
            display: none;
        }
    </style>
</head>
<body>
    <h1>AWS AppConfig Demo</h1>
    
    <div class="feature feature-feature1 {% if feature1 != 'true' %}disabled{% endif %}">
        <h2>Feature 1</h2>
        <p>This section is visible when feature1 is "true".</p>
    </div>
    
    <div class="feature feature-feature2 {% if feature2 != 'true' %}disabled{% endif %}">
        <h2>Feature 2</h2>
        <p>This section is visible when feature2 is "true".</p>
    </div>
</body>
</html>
```

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat: add HTML template with feature sections"
```

---

### Task 4: Verify and document

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README.md**

```markdown
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
   pip install -r requirements.txt
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
   python app.py
   ```

4. Open http://localhost:5000 in your browser

## Changing Feature Flags

Update your AppConfig configuration in AWS Console:
```json
{
  "feature1": "true",
  "feature2": "true"
}
```

Refresh the page to see changes (new configuration is fetched on each request).
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup instructions"
```

---

## Execution

**Plan complete and saved to `docs/superpowers/plans/2025-04-25-appconfig-demo-plan.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**