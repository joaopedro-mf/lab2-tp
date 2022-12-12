import numpy as np
import base64
import cv2
import requests
import base64
import json
import cv2

API_URL_HEADDECT = None

def getInfoApiHEADDECT():
    url = "https://jsonblob.com/api/jsonBlob/1051248574398218240"

    response = requests.request("GET", url)

    return response.json()["HEADTRACK_MLSERVER"]

def getDataEncodeFormat(image):
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode()

def sendImageApi(image):
    global API_URL_HEADDECT
    if API_URL_HEADDECT is None:
        API_URL_HEADDECT = getInfoApiHEADDECT()

    data = getDataEncodeFormat(image)

    face_response = requests.post(
        API_URL_HEADDECT + '/internalBus',
        data = {  
            "image": data
          },
    )
    return face_response.json()

