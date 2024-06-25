# How to run program

## Install Poetry

If you haven't installed Poetry yet, you can do so by following the instructions on the Poetry website.

## Install project dependencies

```bash
poetry install
```

## Create configuration file

Create a config.yml file in the project root with the following content:

```yaml
upscale_url: "https://example.com/upscale"
api_key: "example_key"
```

## Running the Program
To run the program, use the following command:

```bash
poetry run python entrypoint.py
```

# lazaza-assessment

Your goal is to write Python code that delivers the service described in the ticket below.  You should write code that you would feel comfortable submitting for code review and deploying to production. 

Please use this repository to implement the ticket.  For submission, either fork the repo and provide the url, or zip your local repo and send to your interviewer. 

Please spend no more than two hours on this project. 

### LA-1234
**Title:** Implement the Image Upscaling Processor

**Description:** We need to create a processor that can take incoming image upscaling messages, upscale them using a 3rd party API, and submit them to our image service.  The following components have already been implemented: 

* Image Message Queue: A client to the queue is provided in src/clients/queue_client.py.  Instantiating “QueueClient” will create a connection to the queue and calling “pop()” will de-queue a message.  The message is stored and returned as a dictionary with the following attributes: 
    * width: int – the requested width of the image 
    * height: int – the requested height of the image 
    * image_data: str - base64 encoded string of the png image 
* Image Upscaler: An HTTP web service exists for upscaling images. To upscale, submit a POST request to (https://lazazaai00imgageresizer00.azurewebsites.net/api/upscale) with the following fields in the json body of the request 
    * access_token: str – the api access token provided to you 
    * new_height: int – the desired height of the image 
    * new_width: int – the desired width of the image 
    * base64_image: str – the base64 encoded string of the image 
    * **Response**: json, where the field “base64_image” is the base64 encoded string of the png image 
* Image Service: A service to submit the upscaled image to.  A client is provided in src/clients/image_service_client.py.  Instantiating “ImageServiceClient” will create a connection to the image service and calling “post_image()” will submit the image, a status code of 200 indicating a successful submission.  ImageService.post_image() takes in the image as “bytes”. 


The processor should utilize these existing services & clients to upscale images as it receives them from the queue.  The end result of this ticket should be a modification to `entrypoint.py` (and any additional code files you create) that when run will continuously receive messages from the queue, perform upscaling, and post them to the image service.  To verify output, we will run `python entrypoint.py` from the project root.