# OpenFeature Refactor Design

## Overview

Refactor the feature flag demo application to use OpenFeature SDK as the standard flag evaluation interface. This enables vendor-neutral flag evaluation and makes it easy to swap or add backend providers.

**Goal:** Support both AWS AppConfig and Unleash backends through OpenFeature's standardized API.

## Current Architecture

```
app.py → ConfigProvider (abstract)
           ├── UnleashProvider (custom, uses UnleashClient)
           └── AppConfigProvider (custom, uses boto3 appconfigdata)
```

## Target Architecture

```
app.py → openfeature.api.get_client()
           ├── UnleashProvider (from openfeature-provider-unleash)
           └── AwsAppConfigProvider (new, implements AbstractProvider using boto3)
```

## Components

### 1. Unleash Provider (openfeature-provider-unleash)

Use the official `openfeature-provider-unleash` package (v0.1.2+).

**Configuration:**
```python
from openfeature.contrib.provider.unleash import UnleashProvider

provider = UnleashProvider(
    url="https://us.app.getunleash.io/uspp0513/api/",
    app_name="unleash-onboarding-python",
    api_token=api_key,
)
provider.initialize()
```

**API Keys:** Continue using `UNLEASH_API_KEYS` dict in `app.py`, keyed by environment.

### 2. AWS AppConfig Provider (Custom Implementation)

No official Python OpenFeature provider exists for AppConfig. Build a custom provider implementing `AbstractProvider`.

**File:** `aws_appconfig_provider.py` (new file)

**Key Methods:**
- `get_metadata()` → return provider name
- `resolve_boolean_details(flag_key, default_value, evaluation_context)` → fetch config from AppConfig, return FlagResolutionDetails

**Implementation Details:**
- Use `boto3.client("appconfigdata")` for AppConfig Data API
- Call `start_configuration_session` on first access to establish session (uses `env` parameter)
- Call `get_latest_configuration` with session token
- Parse JSON config, look up `flag_key` in format `config[flagName]["enabled"]` (matching current AppConfig structure)
- Cache session token and refresh when needed
- Handle missing flags by returning default value in FlagResolutionDetails

**Configuration parameters:**
- `app_name` (from `APP_CONFIG_APP` env or default)
- `config_name` (from `APP_CONFIG_CONFIG` env or default)
- `region` (from `AWS_REGION` env or default)
- `env` (passed at evaluation time via evaluation_context or method param)

**Note on environment:** Unlike Unleash which uses API keys per environment, AppConfig uses environment as a parameter in `start_configuration_session`. The environment will be passed when fetching config.

### 3. App Changes (app.py)

**Remove:**
- `ConfigProvider` abstract class
- Custom `UnleashProvider` and `AppConfigProvider` classes
- Direct provider imports

**Add:**
- OpenFeature SDK imports
- Provider selection logic using `api.set_provider()`
- Flag evaluation via `client.get_boolean_value()`

**Provider Selection:**
Use `api.set_provider()` per request (matching current behavior):
```python
from openfeature import api

@app.route("/")
def index():
    provider_name = request.args.get("provider", "appconfig")
    env = request.args.get("env", "dev")

    if provider_name == "unleash":
        provider = UnleashProvider(url=..., app_name=..., api_token=UNLEASH_API_KEYS[env])
        provider.initialize()
    else:
        provider = AwsAppConfigProvider(env=env)

    api.set_provider(provider)
    client = api.get_client()

    feature1 = client.get_boolean_value("feature1", False)
    feature2 = client.get_boolean_value("feature2", False)
    # ... render template
```

**Alternative (domain-scoped):** Register both providers once at startup with domains:
```python
api.set_provider(unleash_provider, domain="unleash")
api.set_provider(appconfig_provider, domain="appconfig")
# Then: client = api.get_client(domain=provider_name)
```

### 4. Dependencies (pyproject.toml)

**Add:**
- `openfeature-sdk>=0.8.2`
- `openfeature-provider-unleash>=0.1.2`

**Remove:**
- `unleashclient` (now a transitive dep of openfeature-provider-unleash)

**Keep:**
- `boto3>=1.43.0` (needed for custom AppConfig provider)
- `flask>=3.1.3`

## Flag Evaluation

OpenFeature uses evaluation context and default values:

```python
client = api.get_client()
feature1_enabled = client.get_boolean_value("feature1", False)
```

The second argument is the default value returned if:
- Provider is not configured
- Flag is not found
- Provider returns an error

## Error Handling

OpenFeature SDK handles errors gracefully:
- Provider initialization failures → returns default value, logs error
- Missing flags → returns default value
- AppConfig session expiration → provider re-initializes session

The custom AppConfig provider should:
- Catch boto3 exceptions and return FlagResolutionDetails with default value
- Handle JSON parse errors gracefully
- Handle missing flag keys by returning default

## Testing Strategy

1. **Unit tests for AwsAppConfigProvider:**
   - Test `resolve_boolean_details` with mock boto3 client
   - Test session initialization and token refresh
   - Test error handling (missing flags, API errors)

2. **Integration tests:**
   - Test Unleash provider with real API (or testcontainers)
   - Test AppConfig provider with mocked AppConfig

3. **Manual testing:**
   - Run app, toggle providers via UI dropdown
   - Verify flags evaluate correctly for both backends

## Migration Steps

1. Add OpenFeature SDK and Unleash provider dependencies
2. Create `aws_appconfig_provider.py` with custom provider
3. Update `app.py` to use OpenFeature API
4. Remove old provider classes from `config_provider.py`
5. Delete `config_provider.py` (or repurpose if needed)
6. Test both providers via UI
7. Update README to document new setup

## Success Criteria

- [ ] Both Unleash and AppConfig backends work through OpenFeature
- [ ] Flag evaluation uses `client.get_boolean_value()` standard API
- [ ] Provider selection via UI dropdown still works
- [ ] Error handling returns defaults gracefully
- [ ] Code is cleaner than before (less custom abstraction)
- [ ] README updated with OpenFeature setup instructions
