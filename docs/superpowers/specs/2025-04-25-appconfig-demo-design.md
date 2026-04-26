# AWS AppConfig Demo - Design

## Overview

A simple Python Flask web application that demonstrates AWS AppConfig by fetching feature toggles and conditionally displaying UI sections based on configuration values.

## Functionality

- Backend fetches AppConfig configuration via boto3 AppConfig Data API
- Frontend displays "Feature 1" when `feature1` is `"true"`
- Frontend displays "Feature 2" when `feature2` is `"true"`

## Architecture

```
Browser  →  Flask Backend  →  AWS AppConfig Data API
                ↓
          HTML Template (Jinja2)
                ↓
            Rendered Page
```

## Components

### Backend (app.py)

- Flask application with single route `/`
- Uses boto3 `start_configuration_session()` and `get_configuration()` to fetch config
- Renders HTML template with feature flags passed as variables
- Simple error handling for missing config or AWS errors

### Frontend (templates/index.html)

- Jinja2 template with conditional blocks
- Two sections: "Feature 1" and "Feature 2"
- Simple inline CSS for visual distinction

## Configuration

- No local config files needed
- AppConfig retrieved at request time
- Requires AWS credentials with AppConfig Data API permissions

## Success Criteria

1. Flask app starts without errors
2. Page loads in browser at http://localhost:5000
3. Both features display when config values are "true"
4. Features hide when config values are not "true"
5. Clear error message if AWS config is unavailable