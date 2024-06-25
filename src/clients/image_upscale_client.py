import aiohttp
import logging

class ImageUpscaleClient:
    """
    Client for interacting with the image upscaling service.
    """

    def __init__(self, config: dict):
        self.upscale_url = config['upscale_url']
        self.api_key = config['api_key']
        self.logger = logging.getLogger(__name__)

    async def upscale_image(self, session: aiohttp.ClientSession, new_width: int, new_height: int, base64_image: str) -> dict:
        """
        Upscales an image using the provided upscale service.

        :param session: The aiohttp ClientSession object.
        :param new_width: The desired width of the upscaled image.
        :param new_height: The desired height of the upscaled image.
        :param base64_image: The base64 encoded string of the image.
        :return: A dictionary containing the upscaled image.
        :raises: Raises an exception if the request to the upscaling service fails.
        """
        payload = {
            'access_token': self.api_key,
            'new_width': new_width,
            'new_height': new_height,
            'base64_image': base64_image
        }
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            async with session.post(self.upscale_url, json=payload, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                self.logger.info(f"Successfully upscaled image. New dimensions: {new_width}x{new_height}.")
                return data
        except aiohttp.ClientResponseError as e:
            self.logger.error(f"Error occurred during image upscaling. Status: {e.status}, Message: {e.message}")
            raise
        except aiohttp.ClientError as e:
            self.logger.error(f"Client error occurred during image upscaling: {str(e)}")
            raise
