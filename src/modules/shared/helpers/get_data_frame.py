import io
import pandas as pd
from flask import Request, jsonify
from pandas import DataFrame


def get_data_frame(request: Request) -> DataFrame:
    file = io.BytesIO(request.data)
    try:
        df = pd.read_excel(file, engine="openpyxl")
        return df
    except Exception as e:
        raise Exception(
            "error: Failed to read Excel file. Please check the file format."
        )
