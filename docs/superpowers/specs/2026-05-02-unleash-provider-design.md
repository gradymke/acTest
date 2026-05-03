# Unleash Provider Integration Design

## Overview

Add Unleash as a second feature flag provider alongside the existing AWS AppConfig provider. Users can select between providers via a new dropdown, with independent environment selection.

## Architecture

The app will have two independent dropdowns in the UI:
- **Provider selector**: Choose between "AppConfig" and "Unleash" (new)
- **Environment selector**: Choose between "dev", "test", "prod" (existing)

Both values are passed as query parameters (`?provider=unleash&env=dev`). The `app.py` route will:
1. Read `provider` param (default: "appconfig") and `env` param (default: "dev")
2. Instantiate the correct provider based on the `provider` value
3. Call `get_config(env)` and `get_flag_value()` as before

The existing `ConfigProvider` abstract class will be extended with a new `UnleashProvider` class following the same interface.

## UnleashProvider Class

New `UnleashProvider` class in `config_provider.py`:

```python
class UnleashProvider(ConfigProvider):
    def __init__(self, api_keys: dict, app_name: str = "unleash-onboarding-python"):
        self.app_name = app_name
        self.api_keys = api_keys  # {"dev": "key1", "test": "key2", "prod": "key3"}
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

The `api_keys` dict is where you'll paste your Unleash API keys. The client initializes per-request as specified.

## App.py Changes

The `app.py` will be updated to:
1. Import both providers
2. Read `provider` query param to select which provider to use
3. Instantiate the correct provider class

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

## Template Changes (index.html)

Add a new provider selector dropdown above/beside the environment selector. Both dropdowns will be independent and submit the form on change.

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
    ...
</div>
```

Each form preserves the other's value via hidden inputs so they work independently.

## Key Design Decisions

1. **Approach**: Extend existing `ConfigProvider` abstract class pattern (Approach 1)
2. **Provider + Environment**: Independent dropdowns, both passed as query params
3. **API Keys**: Dictionary keyed by environment, paste keys into `UNLEASH_API_KEYS` in `app.py`
4. **Unleash Initialization**: Per-request (as requested), not at app startup
