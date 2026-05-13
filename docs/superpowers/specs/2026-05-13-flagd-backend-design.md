# flagd Backend Integration Design

**Date:** 2026-05-13
**Branch:** flagd

## Overview

Add flagd as a third feature flag provider option alongside the existing AWS AppConfig and Unleash backends. The flagd services run locally via gRPC; no cloud credentials or network calls are required.

## Architecture

No new abstractions are introduced. The change extends the existing `get_provider()` factory in `app.py` with a `"flagd"` branch, following the same pattern used for `"unleash"` and `"appconfig"`.

## Components Changed

### `pyproject.toml`
Add `openfeature-provider-flagd` to the `dependencies` list.

### `app.py`
- Import `FlagdProvider` from `openfeature_provider_flagd`
- Add a port map constant:
  ```python
  FLAGD_PORTS = {"dev": 8013, "test": 8023, "prod": 8033}
  ```
- Add a `"flagd"` branch in `get_provider()`:
  ```python
  elif provider_name == "flagd":
      port = FLAGD_PORTS.get(env, 8013)
      provider = FlagdProvider(host="localhost", port=port)
  ```
- No shutdown needed — local gRPC connection has no cloud SDK lifecycle to clean up.

### `templates/index.html`
Add a third option to the provider `<select>`:
```html
<option value="flagd" {% if provider == 'flagd' %}selected{% endif %}>flagd</option>
```

## Data Flow

Request → Flask → `get_provider("flagd", env)` → `FlagdProvider(host="localhost", port=<env-port>)` → gRPC → local flagd daemon → flag value returned via `client.get_boolean_value(...)` (call site unchanged).

## Port Mapping

| Environment | Port |
|-------------|------|
| dev         | 8013 |
| test        | 8023 |
| prod        | 8033 |

## Error Handling

Errors from flagd are caught by the existing `try/except` block in the route handler, which already logs and falls back to `False` for both flags.

## Testing

Manual: run the app, select "flagd" from the provider dropdown, switch environments, verify feature1/feature2 reflect the values in `flagd/dev.json`, `flagd/test.json`, `flagd/prod.json`.
