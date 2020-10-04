import numpy as np
import cv2

def preprocessing(image, ksize, can_thres_min, can_thres_max):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_threshold = cv2.adaptiveThreshold(src=image_gray, maxValue=255, \
        adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C, thresholdType=cv2.THRESH_BINARY_INV, blockSize=15, C=6)

    return image_threshold

def draw_lines(image, lines):
    image_lines = np.copy(image)

    for line in lines:
        rho,theta = line
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        cv2.line(image_lines,(x1,y1),(x2,y2),(0,0,255),2)

    return image_lines

def filter_lines(lines):
    def remove_duplicate_lines(lines):
        d_lines = []
        for line in lines:
            rho, theta = line
            add_line = True
            for d_line in d_lines:
                d_rho = d_line[0]
                if not ((rho < (d_rho - 35)) or (rho > (d_rho + 35))):
                    add_line = False
            if add_line:
                d_lines.append(line)
        return d_lines

    def keep_sudoku_lines(lines):
        lines.sort()
        sudoku_lines = lines
        rhos = []
        index, deviation = 0, 1000

        for line in lines:
            rho, theta = line
            rhos.append(rho)

        for i in np.arange(0, len(lines)-9):
            rho_candidates = rhos[i:i+10]
            rho_diffs = np.asarray(rho_candidates[1:10]) - np.asarray(rho_candidates[0:9])
            rho_diff_mean = int(np.mean(rho_diffs))
            rho_abs_deviations = np.abs(rho_diffs - rho_diff_mean)
            rho_deviation_sum = np.sum(rho_abs_deviations)

            if deviation > rho_deviation_sum:
                index, deviation = i, rho_deviation_sum
                sudoku_lines = lines[i:i+10]
            """print(i)
            print("candidates: " + str(rho_candidates))
            print("diffs: " + str(rho_diffs))
            print(rho_diff_mean)
            print(rho_abs_deviations)
            print(rho_deviation_sum)"""
        print(sudoku_lines)
        return sudoku_lines

    vertical_lines=[]
    horizontal_lines=[]

    # Keep horizontal/vertical lines
    for line in lines:
        rho, theta = line[0]
        if ((theta > 1.5) and (theta < 1.7)):
            horizontal_lines.append((rho, theta))
        elif ((theta > -0.05) and (theta < 0.05)):      
            vertical_lines.append((rho, theta))

    # Filter out similar lines
    horizontal_lines = remove_duplicate_lines(horizontal_lines)
    vertical_lines = remove_duplicate_lines(vertical_lines)

    # Keep sudoku field lines
    horizontal_lines = keep_sudoku_lines(horizontal_lines)
    vertical_lines = keep_sudoku_lines(vertical_lines)
    
    return horizontal_lines, vertical_lines


#cap = cv2.VideoCapture(0)
image = cv2.imread("sudoku2.JPG")
image_prep = preprocessing(image, (5,5), 40, 100)

# Line detection
lines = cv2.HoughLines(image_prep, 1, np.pi/180, 260)

# Filter Lines
horizontal_lines, vertical_lines = filter_lines(lines)

# Draw Lines
image_lines = draw_lines(image, horizontal_lines)
image_lines = draw_lines(image_lines, vertical_lines)

ret_val = True

while ret_val:
    #ret_val, input = cap.read()

    #cv2.imshow("Original", image)
    cv2.imshow("Image Prep", image_prep)
    cv2.imshow("Image lines", image_lines)    

    key = cv2.waitKey(1)
    if (key == 27):
        break
    if (key == 43):
        upper_bound[0] += 1
    if (key == 45):
        upper_bound[0] -= 1