from contextlib import asynccontextmanager
from typing import Optional

import aiohttp


class AIOHTTPClientSession:
    from .session import CRSession

    def __init__(self, session: CRSession):
        self.session = session
        self.client: aiohttp.ClientSession | None = None

    async def initialize_aiohttp_session(
        self, headers=None, connector=None, timeout=None
    ):
        """
        Initializes the aiohttp.ClientSession.
        """
        if not self.client:
            self.client = aiohttp.ClientSession(
                headers=headers or self.session.headers,
                connector=connector,
                timeout=timeout or aiohttp.ClientTimeout(total=30),
            )

    async def close_aiohttp_session(self):
        """
        Closes the aiohttp.ClientSession if it exists.
        """
        if self.client:
            await self.client.close()
            self.client = None

    async def do_cr_fetch(
        self, api_url: str, data: Optional[dict] = None, method: Optional[str] = None
    ):
        from src.services.shared import logger

        try:
            if not self.client:
                raise Exception("Client not initialized")
            csrf = self.session.csrf_token
            crsd = self.session.myCookies.get("crsd")
            crud = self.session.myCookies.get("crud")
            headers = {
                **self.session.myHeaders,
                "cookie": f"csrf-token={csrf}; tzoffset=300; crsd={crsd}; crud={crud}",
            }
            if not data:
                return await self.client.get(api_url, headers=headers)
            if method == "PUT":
                return await self.client.put(api_url, json=data, headers=headers)
            return await self.client.post(api_url, json=data, headers=headers)
        except Exception as e:
            logger.error(
                f"An error occurred while making POST request to {api_url}: {e}"
            )

    @asynccontextmanager
    async def managed_session(self, headers=None, connector=None, timeout=None):
        """
        Context manager for the aiohttp.ClientSession.
        """
        await self.initialize_aiohttp_session(headers, connector, timeout)
        try:
            yield
        finally:
            await self.close_aiohttp_session()
