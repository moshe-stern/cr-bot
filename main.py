import os

from dotenv import load_dotenv
from flask import Flask

from src.cr_playwright_modules.auth_settings.controller import auth_settings

load_dotenv()
app = Flask(__name__)
app.register_blueprint(auth_settings)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=os.getenv("DEVELOPMENT"))
