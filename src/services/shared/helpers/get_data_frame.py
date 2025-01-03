import io

import pandas as pd
from flask import Request, jsonify
from openpyxl.reader.excel import load_workbook
from pandas import DataFrame


def get_data_frame(file_data: bytes) -> DataFrame:
    file = io.BytesIO(file_data)
    try:
        df = pd.read_excel(file, engine="openpyxl")
        return df
    except Exception as e:
        raise Exception(
            "error: Failed to read Excel file. Please check the file format."
        )
