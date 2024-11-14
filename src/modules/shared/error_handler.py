import os
from flask import request, jsonify, abort


def register_error_handlers(app):
    @app.before_request
    def before_request():
        if request.headers.get("X-Secret-Key") != os.getenv("SECRET_KEY"):
            abort(403)

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "An unexpected error occurred"}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        status_code = getattr(e, "code", 500)
        return jsonify({"error": str(e)}), status_code
