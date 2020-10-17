import cv2
import io
import requests
import json

def request_ocr(image, api_key):
    # Encode and compress Image
    _, compressed_image = cv2.imencode(".jpg", image, [1, 100])
    # Get bytes of image
    image_bytes = io.BytesIO(compressed_image)
    # send POST request to OCR API and receive result
    response = requests.post(url="https://api.ocr.space/parse/image", files = {"field.jpg": image_bytes}, data = {"apikey": api_key, "ocrengine": 2, "scale": True})
    # "unwrap" result and return the relevant information
    response_content = json.loads(response.content.decode())
    #print(str(response_content))
    parsed_text = response_content.get("ParsedResults")[0].get("ParsedText")

    return parsed_text

def recognize_digit_ocr_space(image, api_key, i, j):
    digits = ["1","2","3","4","5","6","7","8","9"]
    ocr_result = request_ocr(image, api_key)
    result = 0
    #print("Result: " + str(ocr_result))
    try:
        if ocr_result in digits:
            result = int(ocr_result)
        elif ocr_result == "":
            result = 0
        else: raise Exception("OCR Error")
    except Exception as e:
        print(e.args)
    return result, i, j
