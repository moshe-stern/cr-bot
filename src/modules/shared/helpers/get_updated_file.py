import io
from ast import Bytes

import pandas as pd
from pandas import DataFrame


def get_updated_file(
    df: DataFrame, updated_settings: list[bool], col_name: str
) -> io.BytesIO:
    df["update"] = df.apply(
        lambda row: (
            "Yes"
            if row[col_name] in updated_settings
            and all(updated_settings[row[col_name]])
            else "No"
        ),
        axis=1,
    )
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output
