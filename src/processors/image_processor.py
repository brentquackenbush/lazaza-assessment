import asyncio
import logging
import aiohttp
import base64
from jsonschema import validate, exceptions as jsonschema_exceptions
from .abstract_processor import AbstractProcessor

class ImageProcessor(AbstractProcessor):
    def __init__(self, queue_client, image_upscale_client, image_service_client, config):
        self.queue_client = queue_client
        self.image_upscale_client = image_upscale_client
        self.image_service_client = image_service_client
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.no_message_delay = config.get('no_message_delay', 5)  # Delay in seconds when no messages are in the queue

    def validate_message(self, message):
        schema = {
            "type": "object",
            "properties": {
                "width": {"type": "integer"},
                "height": {"type": "integer"},
                "image_data": {"type": "string"}
            },
            "required": ["width", "height", "image_data"]
        }
        validate(instance=message, schema=schema)

    async def process_message(self, session, message):
        try:
            self.validate_message(message)
            # Extract and convert data
            image_data = message.get('image_data')
            new_width = message.get('width')
            new_height = message.get('height')

            # Upscale the image
            upscaled_image = await self.image_upscale_client.upscale_image(
                session=session,
                new_width=new_width,
                new_height=new_height,
                base64_image=image_data
            )

            # Process the upscaled image
            upscaled_image_data_bytes = base64.b64decode(upscaled_image['base64_image'])
            self.image_service_client.post_image(image=upscaled_image_data_bytes)

        except jsonschema_exceptions.ValidationError as e:
            self.logger.error(f"Validation error: {e}")
        except Exception as e:
            self.logger.error(f"Error processing image: {e}")

    async def process(self):
        async with aiohttp.ClientSession() as session:
            while True:
                message = self.queue_client.pop()
                if not message:
                    self.logger.info("No more messages in the queue. Waiting before retrying.")
                    await asyncio.sleep(self.no_message_delay)
                    continue

                await self.process_message(session, message)
