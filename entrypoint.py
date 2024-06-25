import argparse
import yaml
import asyncio
import logging
from src.clients.queue_client import QueueClient
from src.clients.image_service_client import ImageServiceClient
from src.clients.image_upscale_client import ImageUpscaleClient
from src.processors.image_processor import ImageProcessor

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Upscale images from the queue')
    parser.add_argument('-c', '--config', default='config.yml')
    return parser.parse_args()

def load_configuration(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def initialize_clients(config):
    queue_client = QueueClient()
    upscale_client = ImageUpscaleClient(config)
    image_service_client = ImageServiceClient()
    return queue_client, upscale_client, image_service_client

def main():
    logger = setup_logging()
    args = parse_arguments()
    config = load_configuration(args.config)

    queue_client, upscale_client, image_service_client = initialize_clients(config)
    processor = ImageProcessor(queue_client, upscale_client, image_service_client, config)

    logger.info("Starting the image processor")
    asyncio.run(processor.process())

if __name__ == "__main__":
    main()
