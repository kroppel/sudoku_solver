import numpy as np
import cv2
from detect_sudoku_hough_transform import extract_sudoku, draw_lines, draw_points
from ocr_api_client import recognize_digit_ocr_space
from ocr_tesseract import recognize_digit_tesseract_ocr
import concurrent.futures
import time
from sudoku_solver import solve_sudoku
from sys import argv

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
                correct.append((i, j, ocr_result[i,j], sudoku[i,j]))
            else:
                incorrect.append((i, j, ocr_result[i,j], sudoku[i,j]))
    return correct, incorrect

def solve_sudoku_from_fields(sudoku, ocr_function):
    # Use tesseract-OCR on every field
    start = time.time()
    sudoku_pf = np.ndarray((9,9), int)
    
    if sudoku is None:
        return None, False, None

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in np.arange(9):
            for j in np.arange(9):
                futures.append(executor.submit(ocr_function, sudoku[i,j], i, j))
        for f in futures:
            result, i, j = f.result()
            sudoku_pf[i,j] = int(result)

        print(sudoku_pf)
    
    stop = time.time()
    exec_time = stop-start

    return sudoku_pf, True, exec_time


input = 0 if len(argv) == 1 else argv[1]
cap = cv2.VideoCapture(input)    # Use video/webcam as input source
#image = cv2.imread("sudoku3.jpg")       # Use image as input source

ret_val = True
sudoku = None
solved = False

# If True, ocr.space API is used, if False, Tesseract OCR is used
use_api = False
correct, incorrect = [], []
intersections, h_lines, v_lines = [], [], []

# while-loop keeps reading images from the source until ret_val is false,
# which means no image has been retrieved from the source
while ret_val:
    if sudoku is None:
        ret_val, image = cap.read()
        ret_val, image = cap.read()


        # Extract Sudoku
        sudoku, intersections, h_lines, v_lines = extract_sudoku(image)
    
    elif not solved:
        # OCR
        sudoku_pf = np.ndarray((9,9), int)
        futures = []

        if use_api:
            sudoku_pf, solved, exec_time = solve_sudoku_from_fields(sudoku, recognize_digit_ocr_space)
        else:
            sudoku_pf, solved, exec_time = solve_sudoku_from_fields(sudoku, recognize_digit_tesseract_ocr)

        print("Execution Time: " + str(exec_time))
        correct, incorrect = evaluate_ocr(sudoku_pf)
        print("Evaluation: " + str(len(correct)) + ", " + str(len(incorrect)))
        #print("Correct: " + str(correct))
        print("Incorrect:" + str(incorrect))

        solve_sudoku(sudoku_pf)

    #image_intersects = draw_points(image, intersections)
    image_lines = draw_lines(image, h_lines)
    image_lines = draw_lines(image_lines, v_lines)

    """for i,j,_,_ in incorrect:
            cv2.imshow(str((i,j)), sudoku[i,j])"""

    # Some visualization of the (intermediate) results

    #cv2.imshow("Image Intersects", image_intersects)
    cv2.imshow("Image Lines", image_lines)


    key = cv2.waitKey(1)
    if (key == 27):
        break