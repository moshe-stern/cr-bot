from flask import Flask

from src.cr_playwright_modules.auth_settings.controller import update_auth_settings

app = Flask(__name__)


@app.route("/auth-settings", methods=["POST"])
def auth_settings():
    return update_auth_settings()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
