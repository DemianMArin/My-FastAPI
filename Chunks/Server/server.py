#!/usr/bin/env python
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
 
quality_webp = 80
counter = 0
format = ".4f"
@app.post('/upload')
async def upload(request: Request):
    start_time = time()
    body_validator = MaxBodySizeValidator(MAX_REQUEST_BODY_SIZE)
    filename = request.headers.get('Filename')
    
    if not filename:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail='Filename header is missing')
    try:
        filepath = os.path.join('./', os.path.basename(filename)) 
        # file_ = FileTarget(filepath, validator=MaxSizeValidator(MAX_FILE_SIZE))
        file_ = ValueTarget()
        data = ValueTarget()
        parser = StreamingFormDataParser(headers=request.headers)
        parser.register('file', file_)
        parser.register('data', data)
        
        async for chunk in request.stream():
            body_validator(chunk)
            parser.data_received(chunk)
    except ClientDisconnect:
        print("Client Disconnected")
    except MaxBodySizeException as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, 
           detail=f'Maximum request body size limit ({MAX_REQUEST_BODY_SIZE} bytes) exceeded ({e.body_len} bytes read)')
    except streaming_form_data.validators.ValidationError:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, 
            detail=f'Maximum file size limit ({MAX_FILE_SIZE} bytes) exceeded') 
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail='There was an error uploading the file') 
   
    if not file_.multipart_filename:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='File is missing')


    bytes_encoded_webp = file_.value
    numpy_decoded_webp = np.frombuffer(bytes_encoded_webp, np.uint8) # From bytes to Numpy
    decoded_webp = cv2.imdecode(numpy_decoded_webp, cv2.IMREAD_COLOR) # Conver to org shape
    print(f"[server] Shape sent: {decoded_webp.shape}")


    _, encoded_webp = cv2.imencode(".webp", decoded_webp, [int(cv2.IMWRITE_WEBP_QUALITY), quality_webp]) # Encoding to Webp
    result_bytes_encoded = encoded_webp.tobytes() # Converting to bytes

    buffer = io.BytesIO(result_bytes_encoded)
    print(f"[server] Org response bytes: {buffer.getbuffer().nbytes}")

    async def chunked_response():
        global counter
        while True:
            chunk = buffer.read(8192)
            if not chunk:
                break
            yield chunk


    print(f"[server] Time: {(time() - start_time):{format}}")
    return StreamingResponse(chunked_response(), media_type='application/octet-stream')
    #return {"message": f"Successfuly uploaded {filename}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
