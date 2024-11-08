import os

from flask import Flask, request, abort, jsonify
from dotenv import load_dotenv
import pandas as pd

if not load_dotenv():
    raise Exception('could not import env file')
app = Flask(__name__)

@app.route('/')
def index():
    return 'hi'
@app.route('/auth-settings', methods=['POST'])
def update():
    if request.headers.get("X-Secret-Key") != os.getenv('SECRET_KEY'):
        abort(403)
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Check if the file is an Excel file
    if not file.filename.endswith('.xlsx'):
        return jsonify({"error": "Invalid file format. Please upload an .xlsx file"}), 400

    try:
        # Read the Excel file using pandas
        df = pd.read_excel(file, engine='openpyxl')

        # Process the DataFrame as needed. For example, converting it to JSON format:
        data = df.to_dict(orient='records')

        # Return the processed data as JSON
        return jsonify({"data": data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000)
