import argparse
import io

import pandas as pd
import requests
import base64
import os

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
parser.add_argument(
    "directory_path",
    default="test-files",
    choices=["test", "stress-test"],
    help="Specify the directory path. Default is 'test-files'.",
)
args = parser.parse_args()
environment = args.environment
test_type = args.directory_path
directory_path = "test-files" if test_type == "test" else "test-files/stress-test"
prod = "https://bulk-auth-update-gsgdb6fsefcfbpbn.eastus-01.azurewebsites.net"
local = "http://localhost:8000"

url = f"{local if environment == 'local' else prod}/authorization"
for filename in os.listdir(directory_path):
    file_path = os.path.join(directory_path, filename)
    try:
        if os.path.isfile(file_path):
            with open(file_path, "rb") as file:
                base64data = base64.b64encode(file.read()).decode("utf-8")
            headers = {
                "X-Secret-Key": os.getenv("SECRET_KEY"),
                "Content-Type": "application/json",
            }
            if "Switch back" in filename:
                filename = filename.replace("Switch back", "").strip()
                print("Switching back: " + os.path.splitext(filename)[0])
            else:
                print(os.path.splitext(filename)[0])
            data = {
                "file": {
                    "$content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "$content": base64data,
                },
                "type": os.path.splitext(filename)[0],
                "instance": "Kadiant",
            }
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                file = io.BytesIO(response.content)
                try:
                    df = pd.read_excel(file, engine="openpyxl")
                except Exception as e:
                    raise Exception(
                        "error: Failed to read Excel file. Please check the file format."
                    )
                if "status" in df.columns:
                    total_count = len(df["status"])
                    success_count = df["status"].eq("Successfully updated").sum()
                    fail_count = df["status"].eq("Failed to update").sum()
                    already_count = df["status"].eq("Already updated").sum()
                    success_count = (
                        (success_count / total_count) * 100 if total_count > 0 else 0
                    )
                    fail_count = (
                        (fail_count / total_count) * 100 if total_count > 0 else 0
                    )
                    already_count = (
                        (already_count / total_count) * 100 if total_count > 0 else 0
                    )
                    if success_count > 0:
                        print(f"{success_count}% Successfully updated")
                    if fail_count > 0:
                        print(f"{fail_count}% Failed to update")
                    if already_count > 0:
                        print(f"{already_count}% already updated")
                    if success_count + fail_count + already_count == 0:
                        print("Something went wrong")
                else:
                    print("The 'Update' column was not found in the Excel file.")
            elif response.status_code == 502:
                raise Exception("Server overloaded")
            else:
                raise Exception(response.json())
    except Exception as e:
        print(f"Error: {e}")
