#!/usr/bin/env python
import os
import sys
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

import httpx
import time
import cv2
import io
import numpy as np
from helper import Teacher

EOS_IP = "100.75.115.13" # EOS IP
TITAN_IP = "100.73.107.81" # Titan IP
MY_COMPUTER ="0.0.0.0"
ip = {1: EOS_IP, 2: TITAN_IP, 3: MY_COMPUTER}
port = "8000"
c = 3 # Computer Selector in which API is running

url =f"http://{ip[3]}:{port}/upload_video"

teacher = Teacher(
        text= "I have a BytesIO object containing the data of an excel document. The library I want to use doesn't support BytesIO and expects a File object instead. How can I take my BytesIO object and convert it into a File object?",
        expression=[1,0,1,0,1,0,1])

counter = 0 
with httpx.Client() as client:
    start = time.time()
    r = client.post(url, json=teacher.dict())
    end = time.time()
    print(f'Time elapsed: {(end - start):.4f} s')
    print(r.status_code)

    if r.status_code == 200:
        result_bytes = io.BytesIO()
        for chunk in r.iter_bytes(chunk_size=8192):
            result_bytes.write(chunk)
            counter += 1
        result_bytes.seek(0)
        print(f"Chunks {counter}")
        print(f"[client] Bytes response: {result_bytes.getbuffer().nbytes}")
        

        with open("result.mp4", "wb") as f:
            f.write(result_bytes.getbuffer())


