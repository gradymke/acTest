from flask import Flask, render_template, request

from config_provider import AppConfigProvider, UnleashProvider

app = Flask(__name__)

# API keys dict - ADD YOUR UNLEASH KEYS HERE
UNLEASH_API_KEYS = {
    "dev": "ultest:dev.a53684dd2e9552bb6dd3a66f15ec5aca17a51e6120f5c8fef58b57a5",
    "test": "ultest:test.e5eebe50480f34fb3c7d47fba786a7378b2c697141b6cef350930b69",
    "prod": "ultest:prod.0ee63ac6861ccd52ac35744cad90827166dadf136c321ad93139ed98",
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

    feature1 = False
    feature2 = False

    try:
        provider.get_config(env)
        feature1 = provider.get_flag_value("feature1")
        feature2 = provider.get_flag_value("feature2")
    except Exception as e:
        print(f"Error fetching config: {e}")
    finally:
        if hasattr(provider, 'close'):
            provider.close()

    return render_template(
        "index.html",
        feature1=feature1,
        feature2=feature2,
        env=env,
        provider=provider_name,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
