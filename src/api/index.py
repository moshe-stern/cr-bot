import aiohttp

from src.classes import CRSession
from src.shared import logger


async def do_cr_post(api_url: str, data: dict, session: CRSession):
    try:
        async with aiohttp.ClientSession(headers=session.myHeaders) as client:
            async with client.post(api_url, json=data) as response:
                if response.ok:
                    logger.info(
                        f"Request to {api_url} succeeded with status {response.status}"
                    )
                    return response
                else:
                    logger.error(
                        f"Request to {api_url} failed with status {response.status}"
                    )
                    return False
    except Exception as e:
        logger.error(f"An error occurred while making POST request to {api_url}: {e}")
        return False
