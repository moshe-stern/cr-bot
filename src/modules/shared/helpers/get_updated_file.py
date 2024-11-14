import io
from ast import Bytes

import pandas as pd
from pandas import DataFrame


def get_updated_file(df: DataFrame, updated_settings: list[bool]) -> io.BytesIO:
    df["update"] = df.apply(
        lambda row: (
            "Yes"
            if row["resource_id"] in updated_settings
            and all(updated_settings[row["resource_id"]])
            else "No"
        ),
        axis=1,
    )
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output
