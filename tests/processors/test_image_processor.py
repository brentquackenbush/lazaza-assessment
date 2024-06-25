import unittest
from unittest.mock import Mock, patch, AsyncMock
import base64
import json
import os
from jsonschema import ValidationError

from src.processors.image_processor import ImageProcessor

class TestImageProcessor(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.queue_client = Mock()
        self.image_upscale_client = Mock()
        self.image_upscale_client.upscale_image = AsyncMock()
        self.image_service_client = Mock()
        self.config = {'no_message_delay': 5}
        self.processor = ImageProcessor(
            self.queue_client,
            self.image_upscale_client,
            self.image_service_client,
            self.config
        )

        # Load the test image data from the JSON file
        resources_dir = os.path.join(os.path.dirname(__file__), '../resources')
        with open(os.path.join(resources_dir, 'test_image.json'), 'r') as f:
            self.message = json.load(f)

        # Decode the original image bytes from the JSON file
        self.original_image_bytes = base64.b64decode(self.message['image_data'])

    @patch('aiohttp.ClientSession')
    async def test_processMessageValidImage_upscaleImageAndPostImageSuccessful200(self, mock_session):
        # Encode the original image bytes to create the upscaled image string for the mock return value
        upscaled_image = base64.b64encode(self.original_image_bytes).decode('utf-8')
        self.image_upscale_client.upscale_image.return_value = {
            'base64_image': upscaled_image
        }

        await self.processor.process_message(mock_session.return_value, self.message)

        self.image_upscale_client.upscale_image.assert_called_once_with(
            session=mock_session.return_value,
            new_width=self.message['width'],
            new_height=self.message['height'],
            base64_image=self.message['image_data']
        )
        self.image_service_client.post_image.assert_called_once_with(
            image=base64.b64decode(upscaled_image)
        )

    @patch('aiohttp.ClientSession')
    async def test_processMessageInvalidSchema_returnValidationError(self, mock_session):
        self.processor.validate_message = Mock(side_effect=ValidationError("Invalid message"))

        await self.processor.process_message(mock_session.return_value, self.message)

        self.processor.validate_message.assert_called_once_with(self.message)
        self.image_upscale_client.upscale_image.assert_not_called()
        self.image_service_client.post_image.assert_not_called()

    @patch('aiohttp.ClientSession')
    async def test_processMessageUpscaleImageFails_exceptionCaught(self, mock_session):
        self.processor.validate_message = Mock(return_value=None)
        self.image_upscale_client.upscale_image.side_effect = Exception("Upscaling error")

        await self.processor.process_message(mock_session.return_value, self.message)

        self.processor.validate_message.assert_called_once_with(self.message)
        self.image_upscale_client.upscale_image.assert_called_once_with(
            session=mock_session.return_value,
            new_width=self.message['width'],
            new_height=self.message['height'],
            base64_image=self.message['image_data']
        )
        self.image_service_client.post_image.assert_not_called()

if __name__ == '__main__':
    unittest.main()
