import numpy as np
import cv2
from sympy.solvers import solve
from sympy import Symbol


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

def draw_points(image, points):
    if points is None:
        return image

    image_points = np.copy(image)

    for line in points:
        for point in line:
            cv2.circle(image_points, point, 3, (0, 255, 0), 5)

    return image_points

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

def get_intersections(h_lines, v_lines):
    if (len(h_lines) != 10) or (len(v_lines) != 10):
        return None

    intersections = np.ndarray((10,10), tuple)

    for i in np.arange(0, 10):
        h_line = h_lines[i]
        for j in np.arange(0, 10):
            v_line = v_lines[j]
            h_rho, h_theta = h_line
            v_rho, v_theta = v_line
            x_i, y_i = 0, 0

            if (v_theta == 0):
                x_i = v_rho
            else:
                x_i = ((h_rho * np.sin(v_theta)) - (v_rho * np.sin(h_theta))) / \
                    ((np.cos(h_theta) * np.sin(v_theta)) - (np.cos(v_theta) * np.sin(h_theta)))
            y_i = ((h_rho / np.sin(h_theta)) - (x_i * (np.cos(h_theta) / np.sin(h_theta))))
            
            intersections[i,j] = (x_i, y_i)

    return intersections

def extract_fields(image, intersections):
    if intersections is None:
        return None

    fields = np.ndarray((10,10), np.ndarray)

    for i in np.arange(0, 9):
        for j in np.arange(0, 9):
            upper_left = intersections[i,j]
            upper_right = intersections[i,j+1]
            lower_left = intersections[i+1,j]
            lower_right = intersections[i+1,j+1]
            
            fields[i,j] = image[int(np.max((upper_left[1], upper_right[1]))):int(np.min((lower_left[1], lower_right[1]))), \
                int(np.max((upper_left[0], lower_left[0]))):int(np.min((upper_right[0], lower_right[0])))]

    return fields

cap = cv2.VideoCapture("sudoku2.mp4")
"""image = cv2.imread("sudoku3.JPG")
image_prep = preprocessing(image, (5,5), 40, 100)

# Line detection
lines = cv2.HoughLines(image_prep, 1, np.pi/180, 260)

# Filter Lines
horizontal_lines, vertical_lines = filter_lines(lines)

# Get intersections
intersections = get_intersections(horizontal_lines, vertical_lines)

# Extract fields
fields = extract_fields(image, intersections)


# Draw Lines
image_lines = draw_lines(image, horizontal_lines)
image_lines = draw_lines(image_lines, vertical_lines)
image_intersects = draw_points(image_lines, intersections)"""

ret_val = True

while ret_val:
    ret_val, image = cap.read()

    image_prep = preprocessing(image, (5,5), 40, 100)

    # Line detection
    lines = cv2.HoughLines(image_prep, 1, np.pi/180, 260)

    # Filter Lines
    horizontal_lines, vertical_lines = filter_lines(lines)

    # Get intersections
    intersections = get_intersections(horizontal_lines, vertical_lines)

    # Extract fields
    fields = extract_fields(image, intersections)


    # Draw Lines
    image_lines = draw_lines(image, horizontal_lines)
    image_lines = draw_lines(image_lines, vertical_lines)
    image_intersects = draw_points(image_lines, intersections)

    #cv2.imshow("Original", image)
    #cv2.imshow("Image Prep", image_prep)
    cv2.imshow("Image Intersects", image_intersects)
    #cv2.imshow("Field 8,8", fields[8,8])

    key = cv2.waitKey(1)
    if (key == 27):
        break
    if (key == 43):
        upper_bound[0] += 1
    if (key == 45):
        upper_bound[0] -= 1