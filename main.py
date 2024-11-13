import os

from dotenv import load_dotenv
from flask import Flask

from src.modules.auth_settings.controller import auth_settings
from src.modules.schedule.controller import schedule
from src.modules.shared.error_handler import register_error_handlers

load_dotenv()
app = Flask(__name__)
register_error_handlers(app)
app.register_blueprint(auth_settings)
app.register_blueprint(schedule)


if __name__ == "__main__":
    print(app.url_map)
    app.run(host="0.0.0.0", port=8000, debug=os.getenv("DEVELOPMENT"))
