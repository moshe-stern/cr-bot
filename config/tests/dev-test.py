import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

url = "http://localhost:8000/authorization/test"
headers = {"X-Secret-Key": os.getenv("SECRET_KEY")}
response = requests.post(url, headers={**headers, "Content-Type": "application/json"})
print(json.dumps(response.text, indent=4))
