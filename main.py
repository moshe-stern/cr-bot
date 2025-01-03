import os

from dotenv import load_dotenv
from flask import Flask

from src.controllers.authorization_controller import authorization
from src.controllers.celery_controller import celery_controller
from src.services.shared import logger, register_error_handlers

if not load_dotenv():
    raise Exception("Failed to load dotenv")
app = Flask(__name__)
register_error_handlers(app)
app.register_blueprint(celery_controller)
app.register_blueprint(authorization)


if __name__ == "__main__":
    logger.info(app.url_map)
    app.run(host="0.0.0.0", port=8000, debug=os.getenv("DEVELOPMENT") == "TRUE")
