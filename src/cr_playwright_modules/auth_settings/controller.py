import pandas as pd
from main import app
from src.cr_playwright_modules.auth_settings.resources import CRResource, UpdateType
from src.cr_playwright_modules.auth_settings.services.index import (
    playwright_update_auth_settings,
)
import io
import os
from flask import Flask, request, abort, jsonify, send_file


@app.route("/auth-settings", methods=["POST"])
def update_auth_settings():
    if request.headers.get("X-Secret-Key") != os.getenv("SECRET_KEY"):
        abort(403)
    if not request.data:
        return jsonify({"error": "No file data in the request"}), 400

    try:
        file = io.BytesIO(request.data)
        try:
            df = pd.read_excel(file, engine="openpyxl")
        except Exception as e:
            return (
                jsonify(
                    {
                        "error": "Failed to read Excel file. Please check the file format."
                    }
                ),
                400,
            )
        update_type_str = request.args.get("type")
        if update_type_str not in UpdateType:
            return jsonify({"error": "Not valid update type specified"}), 400
        update_type = UpdateType(update_type_str)
        required_columns = {
            "resource_id",
            f"{update_type}_to_remove",
            f"{update_type}_to_change",
        }
        if not required_columns.issubset(df.columns):
            return (
                jsonify(
                    {
                        "error": f"Missing required columns. Required columns are: {required_columns}"
                    }
                ),
                400,
            )
        resources = [
            CRResource(
                row["resource_id"],
                [
                    str(code).strip()
                    for code in row[f"{update_type}_to_remove"].split(",")
                ],
                [
                    str(code).strip()
                    for code in row[f"{update_type}_to_change"].split(",")
                ],
            )
            for _, row in df.iterrows()
        ]
        updated_settings = playwright_update_auth_settings(resources)
        df["update"] = df.apply(
            lambda row: (
                "Yes"
                if row["resource_id"] in updated_settings
                and updated_settings[row["resource_id"]][0]
                and updated_settings[row["resource_id"]][1]
                else "No"
            ),
            axis=1,
        )
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Sheet1")
        output.seek(0)
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="updated_file.xlsx",
        )

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
