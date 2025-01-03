import asyncio
import os
from flask import Blueprint, Response, jsonify, request
from playwright.async_api import async_playwright
from src.services.celery_tasks import process_update, start_playwright
from src.classes import (
    UpdateType,
)
from src.services.shared import (
    get_json,
    logger,
    divide_list,
    get_resource_arr,
    get_updated_file,
)
import pandas as pd

from src.services.shared import check_required_cols

authorization = Blueprint("authorization", __name__, url_prefix="/authorization")


@authorization.route("", methods=["POST"])
def update() -> tuple[Response, int]:
    data = get_json(request)
    file = data.get("file")
    instance: str = data.get("instance")
    update_type_str: str = data.get("type")
    base64_content: bytes = file.get("$content")
    args = (base64_content, update_type_str, instance)
    task = process_update.apply_async(args=args)
    return jsonify({"task_id": task.id}), 202


# for quick testing when adding new services
if os.getenv("DEVELOPMENT") == "TRUE":

    @authorization.route("/test", methods=["POST"])
    def test():
        async def run_test():
            data = request.files["file"]
            file = pd.read_excel(data)
            update_type = UpdateType.CODES
            check_required_cols(update_type, file)
            payor_resources = get_resource_arr(update_type, file)
            try:
                chunks = divide_list(payor_resources, 20)
                combined_results = {}
                update_results = await start_playwright(
                    chunks, None, "Kadiant", update_type
                )
                for result in update_results:
                    if isinstance(result, Exception):
                        logger.error(f"Error processing chunk: {result}")
                    else:
                        combined_results.update(result)
                get_updated_file(file, combined_results, "resource_id")
                output_folder = "./output"
                os.makedirs(output_folder, exist_ok=True)
                output_file_path = os.path.join(
                    output_folder, os.path.basename("results.csv")
                )
                file.to_csv(output_file_path, index=False)
                print(f"File saved to: {output_file_path}")
                return {"results": combined_results}
            except Exception as e:
                logger.error(e)
                return {"error": "Failed to update"}

        return asyncio.run(run_test())
