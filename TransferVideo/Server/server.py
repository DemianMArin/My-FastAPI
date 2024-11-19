#!/usr/bin/env python
import os
import sys
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

from fastapi import FastAPI, Request, HTTPException, status
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget
from streaming_form_data.validators import MaxSizeValidator
import streaming_form_data
from starlette.requests import ClientDisconnect
from starlette.responses import StreamingResponse
import uvicorn
import os
import numpy as np
import cv2
import io
from time import time
from helper import Teacher

MAX_FILE_SIZE = 1024 * 1024 * 1024 * 4  # = 4GB
MAX_REQUEST_BODY_SIZE = MAX_FILE_SIZE + 1024

app = FastAPI()

class MaxBodySizeException(Exception):
    def __init__(self, body_len: str):
        self.body_len = body_len

class MaxBodySizeValidator:
    def __init__(self, max_size: int):
        self.body_len = 0
        self.max_size = max_size

    def __call__(self, chunk: bytes):
        self.body_len += len(chunk)
        if self.body_len > self.max_size:
            raise MaxBodySizeException(body_len=self.body_len)
 

format = ".4f"
@app.post('/upload_video')
async def upload_video(teacher: Teacher):
    start_time = time()


    print(f"Text: {teacher.text}")

    # path = "Data/video3840x2160.mp4"
    path = "Data/video640x360.mp4"
    with open(path, 'rb') as file:
        video_data = file.read()
        video_buffer = io.BytesIO(video_data)
        print(f"[server] Org response bytes: {video_buffer.getbuffer().nbytes}")


    async def chunked_response():
        global counter
        while True:
            chunk = video_buffer.read(8192)
            if not chunk:
                break
            yield chunk

    print(f"[server] Time: {(time() - start_time):{format}}")
    return StreamingResponse(chunked_response(), media_type='application/octet-stream')


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
