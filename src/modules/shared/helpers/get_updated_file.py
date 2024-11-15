import io
from ast import Bytes
from typing import Union

import pandas as pd
from pandas import DataFrame


def get_updated_file(
    df: DataFrame, updated_settings: dict[int, list[Union[bool, None]]], col_name: str
) -> io.BytesIO:
    df["status"] = df.apply(
        lambda row: (
            "Successfully updated"
            if updated_settings[row[col_name]] == True
            else (
                "Failed to update"
                if updated_settings[row[col_name]] == False
                else "Already updated"
            )
        ),
        axis=1,
    )
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output