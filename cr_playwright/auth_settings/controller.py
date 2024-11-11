import pandas as pd
from cr_playwright.auth_settings.resources import CRResource
from cr_playwright.auth_settings.service import playwright_update_auth_settings, logger
import io
import os
from flask import Flask, request, abort, jsonify, send_file
def update_auth_settings():
    if request.headers.get("X-Secret-Key") != os.getenv('SECRET_KEY'):
        abort(403)
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith('.xlsx'):
        return jsonify({"error": "Invalid file format. Please upload an .xlsx file"}), 400

    try:
        df = pd.read_excel(file, engine='openpyxl')
        resources = [
            CRResource(
                row['resource_id'],
                [str(code).strip() for code in row['codes_to_remove'].split(',')],
                [str(code).strip() for code in row['codes_to_change'].split(',')]
            )
            for _, row in df.iterrows()
        ]
        updated_settings = playwright_update_auth_settings(resources)
        df['update'] = df.apply(
            lambda row: "Yes" if updated_settings[row['resource_id']][0] and updated_settings[row['resource_id']][1] else "No",
            axis=1
        )
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='updated_file.xlsx'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
