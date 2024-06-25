import unittest
from unittest.mock import patch, Mock
import aiohttp

from src.clients.image_upscale_client import ImageUpscaleClient

class TestImageUpscaleClient(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.config = {
            'upscale_url': 'https://test.com/upscale',
            'api_key': 'test_api_key'
        }
        self.client = ImageUpscaleClient(config=self.config)
        self.base64_image = "base64encodedstring"

    @patch('aiohttp.ClientSession.post')
    async def test_upscaleImageWithValidImage_successResponds200(self, mock_post):
        async def mock_json():
            return {'base64_image': 'upscaled_base64encodedstring'}

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = mock_json
        mock_post.return_value.__aenter__.return_value = mock_response

        async with aiohttp.ClientSession() as session:
            response = await self.client.upscale_image(session, 1024, 768, self.base64_image)

        self.assertEqual(response, {'base64_image': 'upscaled_base64encodedstring'})
        mock_post.assert_called_once_with(
            self.config['upscale_url'],
            json={
                'access_token': self.config['api_key'],
                'new_width': 1024,
                'new_height': 768,
                'base64_image': self.base64_image
            },
            headers={'Content-Type': 'application/json'}
        )

    @patch('aiohttp.ClientSession.post')
    async def test_upscaleImageWhenServiceReturns400_responds400ExceptionCaught(self, mock_post):
        mock_response = Mock()
        mock_response.status = 400
        mock_response.raise_for_status = Mock(side_effect=aiohttp.ClientResponseError(
            request_info=Mock(),
            history=(),
            status=400,
            message="Bad Request"
        ))
        mock_post.return_value.__aenter__.return_value = mock_response

        with self.assertRaises(aiohttp.ClientResponseError) as cm:
            async with aiohttp.ClientSession() as session:
                await self.client.upscale_image(session, 1024, 768, self.base64_image)

        self.assertEqual(cm.exception.status, 400)

        mock_post.assert_called_once_with(
            self.config['upscale_url'],
            json={
                'access_token': self.config['api_key'],
                'new_width': 1024,
                'new_height': 768,
                'base64_image': self.base64_image
            },
            headers={'Content-Type': 'application/json'}
        )

if __name__ == '__main__':
    unittest.main()
