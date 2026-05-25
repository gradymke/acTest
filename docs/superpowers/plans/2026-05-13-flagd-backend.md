# flagd Backend Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add flagd as a third feature flag provider option, connecting via gRPC to locally-running flagd daemons on per-environment ports.

**Architecture:** Extend the existing `get_provider()` factory in `app.py` with a `"flagd"` branch using `FlagdProvider(host="localhost", port=<env-port>)`. Add the `openfeature-provider-flagd` dependency and a new `<option>` in the HTML dropdown.

**Tech Stack:** Python, Flask, OpenFeature SDK (`openfeature-sdk`), `openfeature-provider-flagd`, uv (package manager)

---

### Task 1: Add `openfeature-provider-flagd` dependency

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add the dependency**

In `pyproject.toml`, add `openfeature-provider-flagd` to the `dependencies` list:

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
    "openfeature-provider-flagd>=0.1.0",
]
```

- [ ] **Step 2: Sync the venv**

```bash
uv sync
```

Expected: resolves and installs `openfeature-provider-flagd` (and any gRPC deps) with no errors.

- [ ] **Step 3: Verify import works**

```bash
uv run python -c "from openfeature_provider_flagd import FlagdProvider; print('ok')"
```

Expected output: `ok`

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "feat: add openfeature-provider-flagd dependency"
```

---

### Task 2: Write tests for `get_provider()` flagd branch

**Files:**
- Modify: `tests/test_app.py` (create if it doesn't exist)

- [ ] **Step 1: Write failing tests**

Create (or add to) `tests/test_app.py`:

```python
import pytest
from unittest.mock import patch, MagicMock


class TestGetProviderFlagd:
    """Tests for get_provider() flagd branch in app.py"""

    def test_flagd_provider_dev_port(self):
        """get_provider('flagd', 'dev') uses port 8013"""
        with patch("app.FlagdProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            from app import get_provider
            get_provider("flagd", "dev")
            mock_cls.assert_called_once_with(host="localhost", port=8013)

    def test_flagd_provider_test_port(self):
        """get_provider('flagd', 'test') uses port 8023"""
        with patch("app.FlagdProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            from app import get_provider
            get_provider("flagd", "test")
            mock_cls.assert_called_once_with(host="localhost", port=8023)

    def test_flagd_provider_prod_port(self):
        """get_provider('flagd', 'prod') uses port 8033"""
        with patch("app.FlagdProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            from app import get_provider
            get_provider("flagd", "prod")
            mock_cls.assert_called_once_with(host="localhost", port=8033)

    def test_flagd_provider_unknown_env_falls_back_to_dev_port(self):
        """get_provider('flagd', 'unknown') falls back to port 8013"""
        with patch("app.FlagdProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            from app import get_provider
            get_provider("flagd", "unknown")
            mock_cls.assert_called_once_with(host="localhost", port=8013)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_app.py -v
```

Expected: FAIL — `ImportError` or `AttributeError` because `FlagdProvider` is not yet imported in `app.py`.

---

### Task 3: Implement the flagd branch in `app.py`

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Add import and port map**

At the top of `app.py`, add the import alongside the existing provider imports:

```python
from flask import Flask, render_template, request

from openfeature import api
from openfeature.contrib.provider.unleash import UnleashProvider
from openfeature_provider_flagd import FlagdProvider
from aws_appconfig_provider import AwsAppConfigProvider
```

Then add the port map constant after `UNLEASH_URL`/`UNLEASH_APP_NAME`:

```python
FLAGD_PORTS = {"dev": 8013, "test": 8023, "prod": 8033}
```

- [ ] **Step 2: Add the flagd branch to `get_provider()`**

Replace the existing `get_provider` function body so it reads:

```python
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
    elif provider_name == "flagd":
        port = FLAGD_PORTS.get(env, 8013)
        provider = FlagdProvider(host="localhost", port=port)
    else:
        provider = AwsAppConfigProvider(env=env)

    return provider
```

- [ ] **Step 3: Run tests to verify they pass**

```bash
uv run pytest tests/test_app.py -v
```

Expected: all 4 flagd tests PASS.

- [ ] **Step 4: Run full test suite to check for regressions**

```bash
uv run pytest -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_app.py
git commit -m "feat: add flagd provider backend"
```

---

### Task 4: Add flagd option to the HTML dropdown

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Add the option to the provider select**

In `templates/index.html`, find the `<select name="provider" ...>` block (around line 75) and add a third option:

```html
<select name="provider" id="provider" onchange="this.form.submit()">
    <option value="appconfig" {% if provider == 'appconfig' %}selected{% endif %}>AppConfig</option>
    <option value="unleash" {% if provider == 'unleash' %}selected{% endif %}>Unleash</option>
    <option value="flagd" {% if provider == 'flagd' %}selected{% endif %}>flagd</option>
</select>
```

- [ ] **Step 2: Verify the app starts**

```bash
uv run python app.py
```

Expected: Flask starts on port 8000 with no import errors.

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat: add flagd option to provider dropdown"
```
