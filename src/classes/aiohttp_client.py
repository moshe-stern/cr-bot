import aiohttp




class AIOHTTPClientSession:
    from src.classes import CRSession
    def __init__(self, session: CRSession):
        self.session = session
        self.client = None

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

    async def do_cr_post(self, api_url: str, data: dict):
        from src.shared import logger
        try:
            if not self.client:
                raise Exception("Client not initialized")
            csrf = self.session.csrf_token
            crsd = self.session.myCookies.get("crsd")
            crud = self.session.myCookies.get("crud")
            response = await self.client.post(
                api_url,
                json=data,
                headers={
                    **self.session.myHeaders,
                    "cookie": f"csrf-token={csrf}; tzoffset=300; crsd={crsd}; crud={crud}",
                },
            )
            if response.status < 400:
                return response
            else:
                raise Exception(await response.text())
        except Exception as e:
            logger.error(
                f"An error occurred while making POST request to {api_url}: {e}"
            )
            return False
