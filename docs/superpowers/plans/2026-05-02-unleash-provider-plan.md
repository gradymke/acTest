# Unleash Provider Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Unleash as a second feature flag provider alongside AWS AppConfig

**Architecture:** Extend the existing ConfigProvider abstract class with a new UnleashProvider. Add provider selection dropdown to the UI independent of environment selector.

**Tech Stack:** Python, Flask, UnleashClient, boto3

---

### Task 1: Add UnleashProvider to config_provider.py

**Files:**
- Modify: `config_provider.py`

- [ ] **Step 1: Add Unleash import and UnleashProvider class**

Add after the existing imports and before `class AppConfigProvider`:

```python
from UnleashClient import UnleashClient


class UnleashProvider(ConfigProvider):
    def __init__(self, api_keys: dict, app_name: str = "unleash-onboarding-python"):
        self.app_name = app_name
        self.api_keys = api_keys
        self.client = None
        self.config = {}

    def get_config(self, env: str) -> dict:
        api_key = self.api_keys.get(env)
        if not api_key:
            raise ValueError(f"No API key for environment: {env}")

        self.client = UnleashClient(
            url="https://us.app.getunleash.io/uspp0513/api/",
            app_name=self.app_name,
            custom_headers={'Authorization': api_key}
        )
        self.client.initialize_client()
        return self.config

    def get_flag_value(self, flag_name: str) -> bool:
        if not self.client:
            return False
        return self.client.is_enabled(flag_name)
```

- [ ] **Step 2: Run linting to verify syntax**

Run: `cd /Users/bgrady/Development/ai/acTest && python -m py_compile config_provider.py`
Expected: No output (success)

- [ ] **Step 3: Commit**

```bash
git add config_provider.py
git commit -m "feat: add UnleashProvider class extending ConfigProvider"
```

---

### Task 2: Update app.py to support provider selection

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Update imports and add API keys dict**

Replace the current imports and add after `app = Flask(__name__)`:

```python
from flask import Flask, render_template, request
from config_provider import AppConfigProvider, UnleashProvider

app = Flask(__name__)

# API keys dict - ADD YOUR UNLEASH KEYS HERE
UNLEASH_API_KEYS = {
    "dev": "PASTE_DEV_KEY_HERE",
    "test": "PASTE_TEST_KEY_HERE",
    "prod": "PASTE_PROD_KEY_HERE",
}

def get_provider(provider_name):
    if provider_name == "unleash":
        return UnleashProvider(api_keys=UNLEASH_API_KEYS)
    return AppConfigProvider()
```

- [ ] **Step 2: Update the index route**

Replace the `index()` function:

```python
@app.route("/")
def index():
    provider_name = request.args.get("provider", "appconfig")
    env = request.args.get("env", "dev")

    provider = get_provider(provider_name)

    try:
        config = provider.get_config(env)
    except Exception as e:
        config = {"feature1": "false", "feature2": "false"}
        print(f"Error fetching config: {e}")

    return render_template(
        "index.html",
        feature1=provider.get_flag_value("feature1"),
        feature2=provider.get_flag_value("feature2"),
        env=env,
        provider=provider_name,
    )
```

- [ ] **Step 3: Run linting to verify syntax**

Run: `cd /Users/bgrady/Development/ai/acTest && python -m py_compile app.py`
Expected: No output (success)

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: add provider selection support in app.py"
```

---

### Task 3: Update template with provider dropdown

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Add provider selector and update top-section**

Replace the `top-section` div (lines 70-104):

```html
<div class="top-section">
    <div class="provider-selector">
        <form method="get" action="/">
            <input type="hidden" name="env" value="{{ env }}">
            <label for="provider">Provider:</label>
            <select name="provider" id="provider" onchange="this.form.submit()">
                <option value="appconfig" {% if provider == 'appconfig' %}selected{% endif %}>AppConfig</option>
                <option value="unleash" {% if provider == 'unleash' %}selected{% endif %}>Unleash</option>
            </select>
        </form>
    </div>

    <div class="env-selector">
        <form method="get" action="/">
            <input type="hidden" name="provider" value="{{ provider }}">
            <label for="env">Environment:</label>
            <select name="env" id="env" onchange="this.form.submit()">
                <option value="dev" {% if env == 'dev' %}selected{% endif %}>dev</option>
                <option value="test" {% if env == 'test' %}selected{% endif %}>test</option>
                <option value="prod" {% if env == 'prod' %}selected{% endif %}>prod</option>
            </select>
        </form>
    </div>

    <div class="status-card">
        <h3>Current Status</h3>
        <p><strong>Provider:</strong> {{ provider }}</p>
        <p><strong>Environment:</strong> {{ env }}</p>
        <ul>
            <li>
                Feature 1:
                {% if feature1 %}
                    <span class="badge-enabled">✓ Enabled</span>
                {% else %}
                    <span class="badge-disabled">✗ Disabled</span>
                {% endif %}
            </li>
            <li>
                Feature 2:
                {% if feature2 %}
                    <span class="badge-enabled">✓ Enabled</span>
                {% else %}
                    <span class="badge-disabled">✗ Disabled</span>
                {% endif %}
            </li>
        </ul>
    </div>
</div>
```

- [ ] **Step 2: Update title and heading**

Change title from "AWS AppConfig Demo" to "Feature Flag Demo":

```html
<title>Feature Flag Demo</title>
```

And the h1:
```html
<h1>Feature Flag Demo</h1>
```

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat: add provider selection dropdown to UI"
```

---

### Task 4: Update README with Unleash setup instructions

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add Unleash section to README**

Add after the existing content:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add Unleash setup instructions to README"
```

---
