from fastapi import FastAPI, File, UploadFile, Response
import numpy as np
import cv2
import time
import logging
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel
import random
from PIL import Image

class EmptyRequest(BaseModel):
    pass

class Item(BaseModel):
    value: int

send_receive_frame = "/send_receive_frame/"
empty_receive_frame = "/empty_receive_frame/"
send_empty_frame = "/send_empty_frame/"
empty_empty_frame = "/empty_empty_frame/"

resolution = (3090, 1090, 3)

app = FastAPI()
logger = logging.getLogger("server")
DEBUG=False
logging.basicConfig(
        format="%(levelname)7s from %(name)s in %(pathname)s:%(lineno)d: %(message)s",
        level=logging.DEBUG if DEBUG else logging.INFO,
        force=True,
    )

def heavy_processing(img):
    # Simulate heavy processing taking 200 ms
    time.sleep(0.03)
    
    # Replace this with your actual processing logic
    #result = np.random.randint(0, 255, (448, 412, 3), dtype=np.uint8)
    
    #return result
    return None

def random_rect(width=320, height=240):
    """Create an image with 4 vertical rectangles with random colors."""
    # Define the size of each rectangle and the overall image
    rectangle_width = width // 4
    rectangle_height = height
    num_rectangles = 4
    image_width = width
    image_height = rectangle_height

    # Create an empty image array
    image = np.zeros((image_height, image_width, 3), dtype=np.uint8)

    # Fill each rectangle with a random color
    for i in range(num_rectangles):
        color = [random.randint(0, 255) for _ in range(3)]
        if i == num_rectangles-1:
            image[:, i*rectangle_width:width] = color
            break
        else:
            image[:, i*rectangle_width:(i+1)*rectangle_width] = color
        
    return image


counter = 0
format = ".4f"
@app.post(f"{send_receive_frame}")
async def send_receive(file: UploadFile = File(...),):
    global counter
    start_endpoint = time.time()

    # Read the file into memory
    file_bytes = await file.read()

    # Convert bytes to numpy array for image processing
    img_array = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  # Decode image from bytes

    # Check if the image was decoded properly
    if img is None:
        logger.error("Failed to decode image")
        return None

    # Add the heavy processing task to the background
    start_heavy_processing = time.time()
    result = await run_in_threadpool(heavy_processing, img)
    end_heavy_processing = time.time() - start_heavy_processing
    logger.info(f"Heavy processing time: {end_heavy_processing:{format}}")
    counter += 1

    if result is None:
        logger.error("No LivePortrait result")
        result = random_rect(width=resolution[0], height=resolution[1])

    logger.info(f"Shape: {result.shape}")

    array_bytes = result.tobytes()
    logger.info(f"Endpoint time: {time.time() - start_endpoint:{format}}")
    # Return the bytes as a response
    return Response(content=array_bytes, media_type="application/octet-stream")

@app.post(f"{empty_receive_frame}")
async def empty_receive(empty_request: EmptyRequest):
    global counter
    start_endpoint = time.time()

    img=random_rect(width=resolution[0], height=resolution[1])

    # image2s = Image.fromarray(img)
    # image2s.save("output_image.png")
    # Add the heavy processing task to the background
    start_heavy_processing = time.time()
    result = await run_in_threadpool(heavy_processing, img)
    end_heavy_processing = time.time() - start_heavy_processing
    logger.info(f"Heavy processing time: {end_heavy_processing:{format}}")
    counter += 1

    if result is None:
        logger.error("No LivePortrait result")
        result = random_rect(width=resolution[0], height=resolution[1])

    array_bytes = result.tobytes()
    logger.info(f"Endpoint time: {time.time() - start_endpoint:{format}}")
    # Return the bytes as a response
    return Response(content=array_bytes, media_type="application/octet-stream")



@app.post(f"{empty_empty_frame}")
async def empty_empty_frame():
    return {}

 