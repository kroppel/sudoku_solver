import numpy as np
import cv2
from detect_sudoku_hough_transform import extract_sudoku, draw_lines, draw_points
from ocr_api_client import recognize_digit_ocr_space
from ocr_tesseract import recognize_digit_tesseract_ocr
import concurrent.futures
import time

def evaluate_ocr(ocr_result):
    sudoku = np.asarray(
    [[9,0,3,6,0,0,0,8,0],
    [2,0,6,9,0,0,0,0,4],
    [0,1,0,0,5,0,6,0,0],
    [0,9,0,5,0,0,0,1,2],
    [1,8,4,0,0,0,5,7,6],
    [5,6,0,0,0,1,0,4,0],
    [0,0,9,0,8,0,0,2,0],
    [7,0,0,0,0,2,9,0,8],
    [0,2,0,0,0,3,7,0,5]],
    dtype=int)

    correct, incorrect = [], [] 
    for i in np.arange(9):
        for j in np.arange(9):
            if ocr_result[i,j] == sudoku[i,j]:
                correct.append((i,j))
            else:
                incorrect.append((i,j))
    return correct, incorrect



#cap = cv2.VideoCapture("sudoku2.mp4")    # Use video/webcam as input source
image = cv2.imread("sudoku3.JPG")       # Use image as input source

ret_val = True
sudoku = None
solved = False
use_api = False
correct, incorrect = [], []

# while-loop keeps reading images from the source until ret_val is false,
# which means no image has been retrieved from the source
while ret_val:
    if sudoku is None:
        #ret_val, image = cap.read()

        # Extract Sudoku
        sudoku, intersections = extract_sudoku(image)

        
        """cv2.imwrite("OCR_Img_2_1.png", sudoku[2,1])
        cv2.imwrite("OCR_Img_4_0.png", sudoku[4,0])

        break"""
    
    elif not solved:
        start = time.time()
        # OCR
        sudoku_pf = np.ndarray((9,9), int)
        futures = []

        if use_api:
            # Read Api-Key from text file (insert your own here!)
            api_key = open("api_key.txt", "r").readline()

            with concurrent.futures.ThreadPoolExecutor() as executor:
                for i in np.arange(9):
                    for j in np.arange(9):
                        futures.append(executor.submit(recognize_digit_ocr_space, sudoku[i,j], api_key, i, j))
            for f in futures:
                result, i, j = f.result()
                sudoku_pf[i,j] = int(result)
                #print(str(result))
                        
            solved = True
            print(sudoku_pf)

        else:
            # Use tesseract-OCR on every field
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for i in np.arange(9):
                    for j in np.arange(9):
                        futures.append(executor.submit(recognize_digit_tesseract_ocr, sudoku[i,j], i, j))
            for f in futures:
                result, i, j = f.result()
                sudoku_pf[i,j] = int(result)
                #print(str(result))

            solved = True
            print(sudoku_pf)

        stop = time.time()
        print("Execution Time: " + str(stop-start))
        correct, incorrect = evaluate_ocr(sudoku_pf)
        print("Evaluation: " + str(len(correct)) + ", " + str(len(incorrect)))
        print("Correct: " + str(correct))
        print("Incorrect:" + str(incorrect))

    image_intersects = draw_points(image, intersections)
    for i,j in incorrect:
            cv2.imshow(str((i,j)), sudoku[i,j])

    # Some visualization of the (intermediate) results

    cv2.imshow("Image Intersects", image_intersects)


    key = cv2.waitKey(1)
    if (key == 27):
        break