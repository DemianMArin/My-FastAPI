#!/usr/bin/env python

import httpx
import time
import cv2
import io
import numpy as np


# EOS_IP = "100.75.115.13" # EOS IP
# TITAN_IP = "100.73.107.81" # Titan IP
# MY_COMPUTER ="0.0.0.0"
# ip = {1: EOS_IP, 2: TITAN_IP, 3: MY_COMPUTER}
# port = "8000"
# c = 3 # Computer Selector in which API is running

url ='http://127.0.0.1:8000/upload'
img = cv2.imread("test_image.jpg")
# img = cv2.imread("resized_test_image.jpg")
print(f"[client] Org shape: {img.shape}")

quality_webp = 80
_, encoded_webp = cv2.imencode(".webp", img, [int(cv2.IMWRITE_WEBP_QUALITY), quality_webp]) # Encoding to Webp
bytes_encoded_webp = encoded_webp.tobytes() # Converting to bytes

check_bytes = io.BytesIO(bytes_encoded_webp)
print(f"[client] Org bytes: {check_bytes.getbuffer().nbytes}")

files = {'file': ("frame.webp", bytes_encoded_webp, "image/webp")}
headers = {'Filename': 'landscape'}
data = {'data': 'Hello World!'}


counter = 0 
with httpx.Client() as client:
    start = time.time()
    r = client.post(url, data=data, files=files, headers=headers)
    end = time.time()
    print(f'Time elapsed: {(end - start):.4f} s')
    print(r.status_code)

    if r.status_code == 200:
        result_bytes = io.BytesIO()
        for chunk in r.iter_bytes(chunk_size=8192):
            result_bytes.write(chunk)
            counter += 1
        result_bytes.seek(0)
        print(f"[client] Bytes response: {result_bytes.getbuffer().nbytes}")
        
        # numpy_decoded_webp = np.frombuffer(bytes_encoded_webp, np.uint8) # From bytes to Numpy
        # decoded_webp = cv2.imdecode(numpy_decoded_webp, cv2.IMREAD_COLOR) # Convert to original image

        # From bytes to np. Shape
        result_array = np.frombuffer(result_bytes.read(), np.uint8)
        if result_array is not None:
            print(f"Shape {result_array.shape}")

        try:
            result_image = cv2.imdecode(result_array, cv2.IMREAD_COLOR)
            #resutl_image = np.reshape(result_array, (4000,6000,3))
        except Exception as e:
            print(f"Error converting decoding {e}")
        else:
            #cv2.imwrite(f"result_image_{quality_webp}.webp", result_image, [int(cv2.IMWRITE_WEBP_QUALITY), quality_webp])
            print(f"Type image: {type(result_image)}")


