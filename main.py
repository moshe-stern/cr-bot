from flask import Flask
from dotenv import load_dotenv

from cr_playwright.auth_settings.controller import update_auth_settings

if not load_dotenv():
    raise Exception('could not import env file')
app = Flask(__name__)
@app.route('/auth-settings', methods=['POST'])
def update_auth_settings():
    update_auth_settings()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
