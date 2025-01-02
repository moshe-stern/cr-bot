import aiohttp

from src.classes import CRSession
from src.shared import logger


async def do_cr_post(api_url: str, data: dict, session: CRSession):
    try:
        async with aiohttp.ClientSession(headers=session.myHeaders) as client:
            csrf = session.csrf_token
            crsd = session.myCookies.get("crsd")
            crud = session.myCookies.get("crud")
            response = await client.post(
                api_url,
                json=data,
                headers={
                    **session.myHeaders,
                    "cookie": f"csrf-token={csrf}; tzoffset=300; crsd={crsd}; crud={crud}",
                },
            )
            if response.status < 400:
                return response
            else:
                raise Exception(await response.text())
    except Exception as e:
        logger.error(f"An error occurred while making POST request to {api_url}: {e}")
        return False
