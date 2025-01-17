import os

import pandas as pd
from flask import request
from src.classes import UpdateType
from src.services.celery_tasks import handle_updates
from src.services.shared import (check_required_cols, get_resource_arr,
                                 get_updated_file, logger)


async def run_test(update_type: UpdateType, instance: str):
    try:
        data = request.files["file"]
        file = pd.read_excel(data)
        check_required_cols(update_type, file)
        update_results = await handle_updates(
            get_resource_arr(update_type, file), -1, instance, update_type
        )
        if not update_results:
            raise Exception("failed to get update results")
        is_client_id_col = update_type in [
            UpdateType.SCHEDULE,
            UpdateType.BILLING,
            UpdateType.TIMESHEET,
        ]
        key_column = "client_id" if is_client_id_col else "resource_id"
        get_updated_file(file, update_results, key_column)
        output_folder = "./output"
        os.makedirs(output_folder, exist_ok=True)
        output_file_path = os.path.join(output_folder, os.path.basename("results.csv"))
        file.to_csv(output_file_path, index=False)
        print(f"File saved to: {output_file_path}")
        return {"results": update_results}
    except Exception as e:
        logger.error(e)
        return {"error": "Failed to update"}
