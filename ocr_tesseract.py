from pytesseract import image_to_string

def recognize_digit_tesseract_ocr(image, i, j):
    digits = ["1","2","3","4","5","6","7","8","9"]

    result = image_to_string(image, config = r'--psm 10')[0]
    result = result if (result in digits) else "0"

    return result, i, j