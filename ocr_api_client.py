from cv2 import imencode
from io import BytesIO
from requests import post
from json import loads

def request_ocr(image):
    # Read Api-Key from text file (insert your own here!)
    api_key = open("api_key.txt", "r").readline()

    # Encode and compress Image
    _, compressed_image = imencode(".jpg", image, [1, 100])

    # Get bytes of image
    image_bytes = BytesIO(compressed_image)

    # send POST request to OCR API and receive result
    response = post(url="https://api.ocr.space/parse/image", files = {"field.jpg": image_bytes}, data = {"apikey": api_key, "ocrengine": 2, "scale": True})
    
    # "unwrap" result and return the relevant information
    response_content = loads(response.content.decode())
    
    #print(str(response_content))
    parsed_text = response_content.get("ParsedResults")[0].get("ParsedText")

    return parsed_text

def recognize_digit_ocr_space(image, i, j):
    digits = ["1","2","3","4","5","6","7","8","9"]
    ocr_result = request_ocr(image)
    result = 0
    
    try:
        if ocr_result in digits:
            result = int(ocr_result)
        elif ocr_result == "":
            result = 0
        else: raise Exception("OCR Error")
    except Exception as e:
        print(e.args)
    return result, i, j
