import os

from dotenv import load_dotenv
from flask import Flask

from src.modules.authorization.controller import authorization
from src.modules.shared.error_handler import register_error_handlers

load_dotenv()
app = Flask(__name__)
register_error_handlers(app)
app.register_blueprint(authorization)


if __name__ == "__main__":
    print(app.url_map)
    app.run(host="0.0.0.0", port=8000, debug=os.getenv("DEVELOPMENT"))
