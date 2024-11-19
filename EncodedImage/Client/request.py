#!/usr/bin/env python
import os
import sys
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

import numpy as np
import cv2
import requests
import logging
import time
import random
from helper import random_rect, list_info
from typing import Callable, Any, List, Tuple

EOS_IP = "100.75.115.13" # EOS IP
TITAN_IP = "100.73.107.81" # Titan IP
MY_COMPUTER ="0.0.0.0"
ip = {1: EOS_IP, 2: TITAN_IP, 3: MY_COMPUTER}
port = "8000"
c = 3 # Computer Selector in which API is running

send_receive_frame = "/send_receive_frame/"
empty_receive_frame = "/empty_receive_frame/"
send_empty_frame = "/send_empty_frame/"
empty_empty_frame = "/empty_empty_frame/"

resolution = (3090, 1090, 3)

format = ".4f"


logger = logging.getLogger("request")
DEBUG=False
logging.basicConfig(
        format="%(levelname)7s from %(name)s in %(pathname)s:%(lineno)d: %(message)s",
        level=logging.DEBUG if DEBUG else logging.INFO,
        force=True,
    )

   
## Functions for posting frames to API
API_SEND_RECEIVE = f"http://{ip[c]}:{port}{send_receive_frame}" 
def post_send_receive(frame: np.ndarray) -> list[float , str]: # Post for Inference
    #_, img_encoded = cv2.imencode('.jpg', frame)
    _, img_encoded = cv2.imencode('.webp', frame, [int(cv2.IMWRITE_WEBP_QUALITY), 1])
    try: # Try statement to catch if API is running
        start_request = time.time()
        response = requests.post(API_SEND_RECEIVE, files={"file": ("frame.webp", img_encoded.tobytes(), "image/webp")})
        #response = requests.post(API_SEND_RECEIVE, files={"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")})
        end_request = time.time()
        logger.debug(f"{send_receive_frame}: {end_request-start_request:{format}}")
        time_ = end_request-start_request
        from_ = send_receive_frame
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error API: {e}")
        return None
    else:
        if response.status_code != 200: # Check if API response was sucessful
            logger.error(f"Error: {response.reason}") 
            return None
        else:
            array_bytes = response.content
            if array_bytes is not None:
                np_image = np.frombuffer(array_bytes, np.uint8)
                requested_frame = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
                #requested_frame = np.frombuffer(array_bytes, dtype=np.uint8).reshape(resolution)
                return [time_, from_]
            return [time_, from_]
        
API_EMPTY_EMPTY = f"http://{ip[c]}:{port}{empty_empty_frame}" 
def post_empty_empty() -> list[float , str]: # Post for Inference
    try:
        start_request = time.time()
        response = requests.post(API_EMPTY_EMPTY, json={})
        end_request = time.time()
        time_ = end_request-start_request
        from_ = empty_empty_frame
        logger.debug(f"{empty_empty_frame}: {end_request-start_request:{format}}")

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error Second Endpoint: {e}")
        return None
    else:
        if response.status_code != 200:
            logger.error(f"Error Second Endpoint: {response.reason}")
            return None
        else:
            pure_response = response.json()
            return [time_, from_]

            
API_EMPTY_RECEIVE = f"http://{ip[c]}:{port}{empty_receive_frame}" 
def post_empty_receive() -> list[float , str]: # Post for Inference
    try:
        start_request = time.time()
        response = requests.post(API_EMPTY_RECEIVE, json={})
        end_request = time.time()
        time_ = end_request-start_request
        from_ = empty_receive_frame
        logger.debug(f"{empty_receive_frame}: {end_request-start_request:{format}}")

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error Empty frame send: {e}")
        return None
    else:
        if response.status_code != 200:
            logger.error(f"Error Empty frame send: {response.reason}")
            return None
        else:
            array_bytes = response.content
            if array_bytes is not None:
                requested_frame = np.frombuffer(array_bytes, dtype=np.uint8).reshape(resolution)
                return [time_, from_]
            return [time_, from_]

def execute_and_log(func: Callable, func_args: Tuple, iterations: int):
    time_list = []
    from_endpoint_ = None

    for _ in range(iterations):
        info = func(*func_args)
        if info[0] is not None:
            time_list.append(info[0])
            from_endpoint_ = info[1]

    list_info_ = list_info(time_list)
    logger.info(f"From: {from_endpoint_} Avg: {list_info_[0]:{format}} Max: {list_info_[1]:{format}} Min: {list_info_[2]:{format}}")

        
def main():
    def menu():
        print(" r - send_receive \n s - empty_receive \n e - empty_empty \n q - exit")

    while True:
        menu()
        user_input = input("Press a key: ")
        time_list = []
        from_endpoint_ = ""
        if user_input == 'r': # send_receive_frame
            execute_and_log(post_send_receive, (random_rect(width=resolution[1], height=resolution[0]),), 10)

        if user_input == 's': # empty_receive_frame
            execute_and_log(post_empty_receive, (), 10)
 
        if user_input == 'e': # empty_empty_frame
            execute_and_log(post_empty_empty, (), 10)

        elif user_input.lower() == 'q':
            break

if __name__ == "__main__":
    main()
