from flask import Flask, render_template, request

from config_provider import AppConfigProvider

app = Flask(__name__)

provider = AppConfigProvider()


def get_app_config(env):
    return provider.get_config(env)


@app.route("/")
def index():
    env = request.args.get("env", "dev")

    try:
        config = get_app_config(env)
    except Exception as e:
        config = {"feature1": "false", "feature2": "false"}
        print(f"Error fetching config: {e}")

    return render_template(
        "index.html",
        feature1=provider.get_flag_value("feature1"),
        feature2=provider.get_flag_value("feature2"),
        env=env,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
