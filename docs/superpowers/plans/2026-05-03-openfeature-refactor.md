# OpenFeature Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the feature flag demo app to use OpenFeature SDK with both Unleash (via official provider) and AppConfig (via custom provider).

**Architecture:** Replace custom ConfigProvider abstract class with OpenFeature SDK. Use `openfeature-provider-unleash` for Unleash backend. Build custom `AwsAppConfigProvider` implementing `AbstractProvider` for AppConfig backend. Flag evaluation done via `openfeature.api.get_client()`.

**Tech Stack:** openfeature-sdk>=0.8.2, openfeature-provider-unleash>=0.1.2, boto3>=1.43.0, flask>=3.1.3

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `pyproject.toml` | Modify | Add OpenFeature dependencies |
| `aws_appconfig_provider.py` | Create | Custom OpenFeature provider for AppConfig |
| `tests/test_aws_appconfig_provider.py` | Create | Unit tests for custom provider |
| `app.py` | Modify | Use OpenFeature API for flag evaluation |
| `config_provider.py` | Delete | Remove old custom providers |
| `README.md` | Modify | Update documentation |

---

### Task 1: Add OpenFeature Dependencies

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Update pyproject.toml with new dependencies**

```toml
[project]
name = "actest"
version = "0.1.0"
description = "This is a test app for AWS AppConfig"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "boto3>=1.43.0",
    "botocore[crt]>=1.26.0",
    "flask>=3.1.3",
    "openfeature-sdk>=0.8.2",
    "openfeature-provider-unleash>=0.1.2",
]
```

- [ ] **Step 2: Sync dependencies**

Run: `uv sync`
Expected: Packages installed successfully

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "feat: add OpenFeature SDK and Unleash provider dependencies"
```

---

### Task 2: Create Test Infrastructure and Write Failing Tests for AwsAppConfigProvider

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_aws_appconfig_provider.py`

- [ ] **Step 1: Create tests directory structure**

```bash
mkdir -p tests
touch tests/__init__.py
```

- [ ] **Step 2: Write failing tests for AwsAppConfigProvider**

Create `tests/test_aws_appconfig_provider.py`:

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from openfeature.flag_evaluation import FlagResolutionDetails
from aws_appconfig_provider import AwsAppConfigProvider


class TestAwsAppConfigProvider:
    """Tests for AwsAppConfigProvider"""

    @pytest.fixture
    def provider(self):
        return AwsAppConfigProvider(
            app_name="test-app",
            config_name="test-config",
            region="us-west-2",
            env="dev",
        )

    @pytest.fixture
    def mock_boto3_client(self):
        with patch("aws_appconfig_provider.boto3.client") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    def test_get_metadata(self, provider):
        """Test provider metadata returns correct name"""
        metadata = provider.get_metadata()
        assert metadata.name == "AWS AppConfig Provider"

    def test_resolve_boolean_details_flag_enabled(self, provider, mock_boto3_client):
        """Test resolving a boolean flag that is enabled"""
        # Setup mock responses
        mock_boto3_client.start_configuration_session.return_value = {
            "InitialConfigurationToken": "token123"
        }
        mock_boto3_client.get_latest_configuration.return_value = {
            "Configuration": MagicMock(
                read=lambda: b'{"feature1": {"enabled": true}}'
            )
        }

        result = provider.resolve_boolean_details(
            flag_key="feature1",
            default_value=False,
        )

        assert isinstance(result, FlagResolutionDetails)
        assert result.value is True
        assert result.error_code is None

    def test_resolve_boolean_details_flag_disabled(self, provider, mock_boto3_client):
        """Test resolving a boolean flag that is disabled"""
        mock_boto3_client.start_configuration_session.return_value = {
            "InitialConfigurationToken": "token123"
        }
        mock_boto3_client.get_latest_configuration.return_value = {
            "Configuration": MagicMock(
                read=lambda: b'{"feature1": {"enabled": false}}'
            )
        }

        result = provider.resolve_boolean_details(
            flag_key="feature1",
            default_value=True,
        )

        assert result.value is False

    def test_resolve_boolean_details_missing_flag_returns_default(self, provider, mock_boto3_client):
        """Test that missing flags return the default value"""
        mock_boto3_client.start_configuration_session.return_value = {
            "InitialConfigurationToken": "token123"
        }
        mock_boto3_client.get_latest_configuration.return_value = {
            "Configuration": MagicMock(
                read=lambda: b'{"feature1": {"enabled": true}}'
            )
        }

        result = provider.resolve_boolean_details(
            flag_key="nonexistent_flag",
            default_value=False,
        )

        assert result.value is False

    def test_resolve_boolean_details_api_error_returns_default(self, provider, mock_boto3_client):
        """Test that API errors return the default value"""
        mock_boto3_client.start_configuration_session.side_effect = Exception("API Error")

        result = provider.resolve_boolean_details(
            flag_key="feature1",
            default_value=True,
        )

        assert result.value is True  # Returns default
        assert result.error_code is not None

    def test_resolve_boolean_details_caches_session_token(self, provider, mock_boto3_client):
        """Test that session token is cached and reused"""
        mock_boto3_client.start_configuration_session.return_value = {
            "InitialConfigurationToken": "token123"
        }
        mock_boto3_client.get_latest_configuration.return_value = {
            "Configuration": MagicMock(
                read=lambda: b'{"feature1": {"enabled": true}}'
            )
        }

        # First call
        provider.resolve_boolean_details("feature1", False)
        # Second call should reuse the token
        provider.resolve_boolean_details("feature1", False)

        # Should only start session once
        assert mock_boto3_client.start_configuration_session.call_count == 1
        assert mock_boto3_client.get_latest_configuration.call_count == 2

    def test_resolve_string_details_returns_default(self, provider):
        """Test that string details returns default (not implemented for AppConfig)"""
        result = provider.resolve_string_details("feature1", "default")
        assert result.value == "default"

    def test_resolve_integer_details_returns_default(self, provider):
        """Test that integer details returns default (not implemented for AppConfig)"""
        result = provider.resolve_integer_details("feature1", 0)
        assert result.value == 0

    def test_resolve_float_details_returns_default(self, provider):
        """Test that float details returns default (not implemented for AppConfig)"""
        result = provider.resolve_float_details("feature1", 0.0)
        assert result.value == 0.0

    def test_resolve_object_details_returns_default(self, provider):
        """Test that object details returns default (not implemented for AppConfig)"""
        result = provider.resolve_object_details("feature1", {})
        assert result.value == {}
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest tests/test_aws_appconfig_provider.py -v`
Expected: FAIL with "No module named aws_appconfig_provider"

- [ ] **Step 4: Commit test file**

```bash
git add tests/
git commit -m "test: add failing tests for AwsAppConfigProvider"
```

---

### Task 3: Implement AwsAppConfigProvider

**Files:**
- Create: `aws_appconfig_provider.py`

- [ ] **Step 1: Create the AwsAppConfigProvider implementation**

Create `aws_appconfig_provider.py`:

```python
import json
import os
from typing import List, Optional, Union

from openfeature.evaluation_context import EvaluationContext
from openfeature.flag_evaluation import FlagResolutionDetails
from openfeature.hook import Hook
from openfeature.provider import AbstractProvider, Metadata
from openfeature.provider.metadata import Metadata


class AwsAppConfigProvider(AbstractProvider):
    """OpenFeature provider for AWS AppConfig using the AppConfig Data API."""

    def __init__(
        self,
        app_name: str = None,
        config_name: str = None,
        region: str = None,
        env: str = "dev",
    ):
        self.app_name = app_name or os.environ.get(
            "APP_CONFIG_APP", "acTestApplication"
        )
        self.config_name = config_name or os.environ.get(
            "APP_CONFIG_CONFIG", "acSimpleFeatureFlag"
        )
        self.region = region or os.environ.get("AWS_REGION", "us-west-2")
        self.env = env
        self._client = None
        self._session_token = None
        self._config = {}

    def get_metadata(self) -> Metadata:
        return Metadata(name="AWS AppConfig Provider")

    def get_provider_hooks(self) -> List[Hook]:
        return []

    def _get_client(self):
        """Lazily initialize and return the boto3 AppConfig Data client."""
        if self._client is None:
            import boto3

            self._client = boto3.client("appconfigdata", region_name=self.region)
        return self._client

    def _ensure_session(self):
        """Ensure we have a valid session token, starting one if needed."""
        if self._session_token is not None:
            return

        client = self._get_client()
        session_response = client.start_configuration_session(
            ApplicationIdentifier=self.app_name,
            EnvironmentIdentifier=self.env,
            ConfigurationProfileIdentifier=self.config_name,
        )
        self._session_token = session_response["InitialConfigurationToken"]

    def _fetch_config(self):
        """Fetch the latest configuration from AppConfig."""
        self._ensure_session()
        client = self._get_client()

        response = client.get_latest_configuration(
            ConfigurationToken=self._session_token
        )

        # Update session token for next request
        self._session_token = response.get("NextPollConfigurationToken", self._session_token)

        config_content = response["Configuration"]

        if hasattr(config_content, "read"):
            config_content = config_content.read().decode("utf-8")

        if config_content:
            self._config = json.loads(config_content)
        else:
            self._config = {}

    def resolve_boolean_details(
        self,
        flag_key: str,
        default_value: bool,
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[bool]:
        try:
            self._fetch_config()
            # AppConfig structure: {"feature1": {"enabled": true}}
            flag_config = self._config.get(flag_key, {})
            value = flag_config.get("enabled", default_value)
            return FlagResolutionDetails(value=value)
        except Exception as e:
            print(f"Error resolving flag {flag_key}: {e}")
            return FlagResolutionDetails(
                value=default_value,
                error_code="PROVIDER_ERROR",
                error_message=str(e),
            )

    def resolve_string_details(
        self,
        flag_key: str,
        default_value: str,
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[str]:
        return FlagResolutionDetails(value=default_value)

    def resolve_integer_details(
        self,
        flag_key: str,
        default_value: int,
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[int]:
        return FlagResolutionDetails(value=default_value)

    def resolve_float_details(
        self,
        flag_key: str,
        default_value: float,
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[float]:
        return FlagResolutionDetails(value=default_value)

    def resolve_object_details(
        self,
        flag_key: str,
        default_value: Union[dict, list],
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[Union[dict, list]]:
        return FlagResolutionDetails(value=default_value)
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `uv run pytest tests/test_aws_appconfig_provider.py -v`
Expected: PASS (all tests)

- [ ] **Step 3: Commit implementation**

```bash
git add aws_appconfig_provider.py
git commit -m "feat: implement AwsAppConfigProvider for OpenFeature"
```

---

### Task 4: Update app.py to Use OpenFeature API

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Update app.py to use OpenFeature**

Replace contents of `app.py`:

```python
from flask import Flask, render_template, request

from openfeature import api
from openfeature.contrib.provider.unleash import UnleashProvider
from aws_appconfig_provider import AwsAppConfigProvider

app = Flask(__name__)

# API keys dict - ADD YOUR UNLEASH KEYS HERE
UNLEASH_API_KEYS = {
    "dev": "ultest:dev.a53684dd2e9552bb6dd3a66f15ec5aca17a51e6120f5c8fef58b57a5",
    "test": "ultest:test.e5eebe50480f34fb3c7d47fba786a7378b2c697141b6cef350930b69",
    "prod": "ultest:prod.0ee63ac6861ccd52ac35744cad90827166dadf136c321ad93139ed98",
}

UNLEASH_URL = "https://us.app.getunleash.io/uspp0513/api/"
UNLEASH_APP_NAME = "unleash-onboarding-python"


def get_provider(provider_name, env):
    if provider_name == "unleash":
        api_key = UNLEASH_API_KEYS.get(env)
        if not api_key:
            raise ValueError(f"No API key for environment: {env}")

        provider = UnleashProvider(
            url=UNLEASH_URL,
            app_name=UNLEASH_APP_NAME,
            api_token=api_key,
        )
        provider.initialize()
    else:
        provider = AwsAppConfigProvider(env=env)

    return provider


@app.route("/")
def index():
    provider_name = request.args.get("provider", "appconfig")
    env = request.args.get("env", "dev")

    provider = get_provider(provider_name, env)
    api.set_provider(provider)

    client = api.get_client()

    feature1 = False
    feature2 = False

    try:
        feature1 = client.get_boolean_value("feature1", False)
        feature2 = client.get_boolean_value("feature2", False)
    except Exception as e:
        print(f"Error fetching config: {e}")
    finally:
        # Clean up Unleash provider if needed
        if provider_name == "unleash" and hasattr(provider, "shutdown"):
            provider.shutdown()

    return render_template(
        "index.html",
        feature1=feature1,
        feature2=feature2,
        env=env,
        provider=provider_name,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
```

- [ ] **Step 2: Test the app runs**

Run: `uv run app.py`
Expected: Flask app starts on http://localhost:8000

- [ ] **Step 3: Commit changes**

```bash
git add app.py
git commit -m "feat: refactor app.py to use OpenFeature API"
```

---

### Task 5: Remove Old config_provider.py

**Files:**
- Delete: `config_provider.py`

- [ ] **Step 1: Delete the old config_provider.py**

```bash
git rm config_provider.py
```

- [ ] **Step 2: Commit deletion**

```bash
git commit -m "refactor: remove old config_provider.py (replaced by OpenFeature)"
```

---

### Task 6: Update README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README with OpenFeature documentation**

Update `README.md` to reflect the new setup:

```markdown
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
```

- [ ] **Step 2: Commit README changes**

```bash
git add README.md
git commit -m "docs: update README for OpenFeature refactoring"
```

---

### Task 7: Manual Integration Testing

**Files:**
- None (testing only)

- [ ] **Step 1: Test AppConfig provider**

1. Start the app: `uv run app.py`
2. Open http://localhost:8000
3. Select "AppConfig" provider and "dev" environment
4. Verify feature flags display correctly

- [ ] **Step 2: Test Unleash provider**

1. Select "Unleash" provider and "dev" environment
2. Verify feature flags display correctly

- [ ] **Step 3: Test error handling**

1. Disconnect from internet/VPN
2. Refresh page
3. Verify default values are shown (no crashes)

- [ ] **Step 4: Final commit (if any fixes needed)**

```bash
git add -A
git commit -m "fix: final integration fixes for OpenFeature refactor"
```

---

## Success Criteria Checklist

- [ ] `openfeature-sdk` and `openfeature-provider-unleash` in pyproject.toml
- [ ] `aws_appconfig_provider.py` exists with `AwsAppConfigProvider` class
- [ ] Tests pass for `AwsAppConfigProvider`
- [ ] `app.py` uses `openfeature.api.get_client()` for flag evaluation
- [ ] `config_provider.py` is deleted
- [ ] Both Unleash and AppConfig work via provider dropdown
- [ ] README updated with OpenFeature documentation
- [ ] All tests pass: `uv run pytest tests/ -v`
