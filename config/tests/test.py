import argparse
import base64
import io
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

sys.path.append(str(Path(__file__).parent.parent.parent))
from dotenv import load_dotenv

load_dotenv()
parser = argparse.ArgumentParser(
    description="Run the application in a specific environment."
)
parser.add_argument(
    "environment",
    choices=["local", "prod"],
    help="Specify the environment to run the application. Options: local or prod.",
)
args = parser.parse_args()
environment = args.environment
prod = "http://cr-bot.westus2.cloudapp.azure.com"
local = "http://localhost:8000"
url: str = f"{local if environment == 'local' else prod}"
task_ids = []
headers = {"X-Secret-Key": os.getenv("SECRET_KEY")}
choices = ["Service Codes", "Payors", "Schedules", "Billing", "Timesheet"]


def handle_files(test_type: str):
    from src.services.shared import logger

    directory_path = "test-files/" + test_type
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path):
                with open(file_path, "rb") as file:
                    base64data = base64.b64encode(file.read()).decode("utf-8")
                if "Switch back" in filename:
                    filename = filename.replace("Switch back", "").strip()
                    logger.info("Switching back: " + os.path.splitext(filename)[0])
                else:
                    logger.info(os.path.splitext(filename)[0])
                data = {
                    "file": {
                        "$content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "$content": base64data,
                    },
                    "type": os.path.splitext(filename)[0],
                    "instance": (
                        "Attain TSS"
                        if os.path.splitext(filename)[0] == "Billing"
                        else "Kadiant"
                    ),
                }
                response = requests.post(
                    url + "/authorization",
                    headers={**headers, "Content-Type": "application/json"},
                    json=data,
                )
                if response.status_code == 202:
                    data = response.json()
                    task_ids.append(data.get("task_id"))
        except Exception as e:
            logger.error(f"Error: {e}")

        time.sleep(10)
        logger.info("sleeping for 10 seconds")
        while len(task_ids) > 0:
            for task_id in task_ids:
                try:
                    res = requests.get(f"{url}/status/{task_id}", headers=headers)
                    data = res.json()
                    if data.get("state") == "SUCCESS":
                        logger.info(f"Progress: {data.get('progress')}")
                        res2 = requests.get(
                            f"{url}/download/{task_id}", headers=headers
                        )
                        task_ids.remove(task_id)
                        if res2.status_code == 200:
                            downloaded_file = io.BytesIO(res2.content)
                            try:
                                df = pd.read_excel(downloaded_file, engine="openpyxl")
                            except Exception as e:
                                raise Exception(
                                    "error: Failed to read Excel file. Please check the file format."
                                )
                            if "updated" in df.columns:
                                total_count = len(df["updated"])
                                success_count = (
                                    df["updated"].eq("Successfully updated").sum()
                                )
                                fail_count = df["updated"].eq("Failed to update").sum()
                                already_count = (
                                    df["updated"]
                                    .eq(
                                        "Didn't fail, but didn't update fully. Please verify"
                                    )
                                    .sum()
                                )
                                success_count = (
                                    (success_count // total_count) * 100
                                    if total_count > 0
                                    else 0
                                )
                                fail_count = (
                                    (fail_count // total_count) * 100
                                    if total_count > 0
                                    else 0
                                )
                                already_count = (
                                    (already_count // total_count) * 100
                                    if total_count > 0
                                    else 0
                                )
                                if success_count > 0:
                                    print(f"{success_count}% Successfully updated")
                                if fail_count > 0:
                                    print(f"{fail_count}% Failed to update")
                                if already_count > 0:
                                    print(
                                        f"{already_count}% Didn't fail, but didn't update"
                                    )
                                if success_count + fail_count + already_count == 0:
                                    print("Something went wrong")
                            else:
                                print(
                                    "The 'Update' column was not found in the Excel file."
                                )
                        else:
                            raise Exception(res2.json())
                    elif data.get("state") == "FAILURE":
                        logger.info("Task Failed")
                        task_ids.remove(task_id)
                    else:
                        logger.info(f"Progress: {data.get('progress')}")
                        time.sleep(10)
                except Exception as e:
                    logger.error(f"Error: {e}")


for choice in choices:
    handle_files(choice)
