import pandas as pd
from cr_playwright.auth_settings.resources import CRResource
from cr_playwright.auth_settings.service import playwright_update_auth_settings
import io
import os
from flask import Flask, request, abort, jsonify, send_file

app = Flask(__name__)

@app.route('/auth-settings', methods=['POST'])
def update_auth_settings():
    # Secret Key Validation
    if request.headers.get("X-Secret-Key") != os.getenv('SECRET_KEY'):
        abort(403)
    print(request)
    # Check if there is data in the request
    if not request.data:
        return jsonify({"error": "No file data in the request"}), 400

    try:
        # Read the binary data directly and load it into a DataFrame
        file = io.BytesIO(request.data)

        # Attempt to read the Excel file
        try:
            df = pd.read_excel(file, engine='openpyxl')
        except Exception as e:
            return jsonify({"error": "Failed to read Excel file. Please check the file format."}), 400

        # Check if required columns are present
        required_columns = {'resource_id', 'codes_to_remove', 'codes_to_change'}
        if not required_columns.issubset(df.columns):
            return jsonify({"error": f"Missing required columns. Required columns are: {required_columns}"}), 400

        # Create resources list
        resources = [
            CRResource(
                row['resource_id'],
                [str(code).strip() for code in row['codes_to_remove'].split(',')],
                [str(code).strip() for code in row['codes_to_change'].split(',')]
            )
            for _, row in df.iterrows()
        ]

        # Update settings
        updated_settings = playwright_update_auth_settings(resources)

        # Add an 'update' column to the DataFrame based on the update status
        df['update'] = df.apply(
            lambda row: "Yes" if row['resource_id'] in updated_settings and
            updated_settings[row['resource_id']][0] and updated_settings[row['resource_id']][1] else "No",
            axis=1
        )

        # Save updated DataFrame to a BytesIO stream
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        output.seek(0)

        # Return the file as a response
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='updated_file.xlsx'
        )

    except Exception as e:
        # General error handling
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
