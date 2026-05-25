from flask import Flask, render_template, request

from openfeature import api
from openfeature.contrib.provider.unleash import UnleashProvider
from openfeature.contrib.provider.flagd import FlagdProvider
from aws_appconfig_provider import AwsAppConfigProvider
from query_override_provider import QueryParamOverrideProvider

app = Flask(__name__)

# API keys dict - ADD YOUR UNLEASH KEYS HERE
UNLEASH_API_KEYS = {
    "dev": "ultest:dev.a53684dd2e9552bb6dd3a66f15ec5aca17a51e6120f5c8fef58b57a5",
    "test": "ultest:test.e5eebe50480f34fb3c7d47fba786a7378b2c697141b6cef350930b69",
    "prod": "ultest:prod.0ee63ac6861ccd52ac35744cad90827166dadf136c321ad93139ed98",
}

UNLEASH_URL = "https://us.app.getunleash.io/uspp0513/api/"
UNLEASH_APP_NAME = "unleash-onboarding-python"

FLAGD_PORTS = {"dev": 8013, "test": 8023, "prod": 8033}


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


@app.route("/")
def index():
    provider_name = request.args.get("provider", "appconfig")
    env = request.args.get("env", "dev")

    provider = get_provider(provider_name, env)
    wrapped_provider = QueryParamOverrideProvider(provider)
    api.set_provider(wrapped_provider)

    client = api.get_client()

    feature1 = False
    feature2 = False

    try:
        feature1 = client.get_boolean_value("feature1", False)
        feature2 = client.get_boolean_value("feature2", False)
    except Exception as e:
        print(f"Error fetching config: {e}")
    finally:
        if hasattr(provider, "shutdown"):
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
