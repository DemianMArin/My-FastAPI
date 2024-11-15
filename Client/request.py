#!/usr/bin/env python
import numpy as np
import cv2
import requests
import logging
import time
import random

EOS_IP = "100.75.115.13" # EOS IP
TITAN_IP = "100.73.107.81" # Titan IP
ip = {1: EOS_IP, 2: TITAN_IP}
port = "8000"
c = 2 # Computer Selector in which API is running

send_receive_frame = "/send_receive_frame/"
empty_receive_frame = "/empty_receive_frame/"
send_empty_frame = "/send_empty_frame/"
empty_empty_frame = "/empty_empty_frame/"

resolution = (3090, 1090, 3)

logger = logging.getLogger("request")
DEBUG=False
logging.basicConfig(
        format="%(levelname)7s from %(name)s in %(pathname)s:%(lineno)d: %(message)s",
        level=logging.DEBUG if DEBUG else logging.INFO,
        force=True,
    )

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

   
## Functions for posting frames to API
format = ".4f"
API_SEND_RECEIVE = f"http://{ip[c]}:{port}{send_receive_frame}" 
def post_send_receive(frame: np.ndarray): # Post for Inference
    _, img_encoded = cv2.imencode('.jpg', frame)
    try: # Try statement to catch if API is running
        start_request = time.time()
        response = requests.post(API_SEND_RECEIVE, files={"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")})
        end_request = time.time()
        logger.info(f"{send_receive_frame}: {end_request-start_request:{format}}")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error API: {e}")
        pass
    else:
        if response.status_code != 200: # Check if API response was sucessful
            logger.error(f"Error: {response.reason}") 
        else:
            array_bytes = response.content
            if array_bytes is not None:
                requested_frame = np.frombuffer(array_bytes, dtype=np.uint8).reshape(resolution)
                return requested_frame
            return None
        
API_EMPTY_EMPTY = f"http://{ip[c]}:{port}{empty_empty_frame}" 
def post_empty_empty(): # Post for Inference
    try:
        start_request = time.time()
        response = requests.post(API_EMPTY_EMPTY, json={})
        end_request = time.time()
        logger.info(f"{empty_empty_frame}: {end_request-start_request:{format}}")

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error Second Endpoint: {e}")
    else:
        if response.status_code != 200:
            logger.error(f"Error Second Endpoint: {response.reason}")
        else:
            pure_response = response.json()
            
API_EMPTY_RECEIVE = f"http://{ip[c]}:{port}{empty_receive_frame}" 
def post_empty_receive(): # Post for Inference
    try:
        start_request = time.time()
        response = requests.post(API_EMPTY_RECEIVE, json={})
        end_request = time.time()
        logger.info(f"{empty_receive_frame}: {end_request-start_request:{format}}")

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error Empty frame send: {e}")
    else:
        if response.status_code != 200:
            logger.error(f"Error Empty frame send: {response.reason}")
        else:
            array_bytes = response.content
            if array_bytes is not None:
                requested_frame = np.frombuffer(array_bytes, dtype=np.uint8).reshape(resolution)
                return requested_frame
            return None


        
def main():
    def menu():
        print(" r - send_receive \n s - empty_receive \n e - empty_empty \n exit - exit")

    while True:
        menu()
        user_input = input("Press a key: ")
        if user_input == 'r': # send_receive_frame
            for _ in range(10):
                post_send_receive(random_rect(width=resolution[1], height=resolution[0]))
        if user_input == 's': # empty_receive_frame
            for _ in range(1):
                post_empty_receive()
        if user_input == 'e': # empty_empty_frame
            for _ in range(10):
                post_empty_empty()

        elif user_input.lower() == 'exit':
            break

if __name__ == "__main__":
    main()
