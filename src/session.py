from datetime import datetime, timezone
import time
from dataclasses import dataclass
import requests
import os

from src.org import CrORG


@dataclass
class CR_TokenResponse:
    access_token: str
    expires_in: int
    token_type: str
    scope: str
    creation_time: int


class CRSession(requests.Session):
    def __init__(self, org: CrORG, headers=None):
        super().__init__()
        self.org = org
        self._client_secret: str = os.getenv(
            f"CR_API_SECRET_{org.org_str}_{org.org_type}"
        )
        self._client_id: str = os.getenv(f"CR_API_ID_{org.org_str}_{org.org_type}")
        self._api_key: str = os.getenv(f"CR_API_KEY_{org.org_str}_{org.org_type}")
        self._cr_token_response: CR_TokenResponse = None
        self._csrf_token = None
        self._make_crsf_token()
        self.utc_offset = self.set_utc_offset()

    def request(self, method, url, **kwargs):
        headers = kwargs.pop("headers", {})
        # Merge custom headers with the provided headers, custom headers taking precedence
        headers = {**self.myHeaders, **headers}
        return super().request(method, url, headers=headers, **kwargs)

    def _make_access_token(self):
        url = "https://login.centralreach.com/connect/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": "cr-api",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code >= 400:
            raise Exception(
                f"could not get access token status code: {response.status_code}"
            )
        self._cr_token_response = CR_TokenResponse(
            **response.json(), creation_time=time.time()
        )

    def _make_cookies(self):
        url = "https://members.centralreach.com/api/?framework.authtoken"

        payload = {"token": self.cr_token_response.access_token}
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        response = self.post(url, headers=headers, json=payload)
        if response.status_code >= 400:
            raise Exception(
                f"could not get cookies status code: {response.status_code}"
            )

    def _make_crsf_token(self):
        self._make_cookies()
        url = "https://members.centralreach.com/api/?framework.csrf"
        response = self.get(
            url,
        )
        if response.status_code >= 400:
            raise Exception(
                f"could not get cookies status code: {response.status_code}"
            )
        self._csrf_token = response.cookies["csrf-token"]

    def set_utc_offset(self):
        local_time = datetime.now(timezone.utc).astimezone()
        return int(local_time.utcoffset().total_seconds() // 60) * -1

    @property
    def cr_token_response(self) -> CR_TokenResponse:
        if (not self._cr_token_response) or (
            time.time() - self._cr_token_response.creation_time + 30
            >= self._cr_token_response.expires_in
        ):
            self._csrf_token = None
            self._make_access_token()
        return self._cr_token_response

    @property
    def csrf_token(self) -> str:
        if not self._csrf_token:
            self._make_crsf_token()
        return self._csrf_token

    @property
    def external_headers(self) -> dict:
        return {
            "x-api-key": self._api_key,
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.cr_token_response.access_token}",
        }

    @property
    def myHeaders(self) -> dict:
        return {
            "x-api-key": self._api_key,
            "Content-Type": "application/json",
            "x-csrf-token": self._csrf_token,
            "Authorization": f"Bearer {self.cr_token_response.access_token}",
        }

    @property
    def myCookies(self):
        return self.cookies
