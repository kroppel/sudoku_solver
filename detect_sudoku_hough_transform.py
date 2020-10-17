import numpy as np
import cv2

# Preprocesses the given image, returning a binary representation of it
def preprocessing(image):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_threshold = cv2.adaptiveThreshold(src=image_gray, maxValue=255, \
        adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C, thresholdType=cv2.THRESH_BINARY_INV, blockSize=15, C=6)
    
    return image_threshold

# Draws the given lines onto a copy of the given image
# and returns it
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

# Draws the given points onto a copy of the given image
# and returns it
def draw_points(image, points):
    if points is None:
        return image

    image_points = np.copy(image)

    for line in points:
        for point in line:
            cv2.circle(image_points, point, 3, (0, 255, 0), 5)

    return image_points

# Filters out irrelevant lines, returning the ten lines
# that belong to the sudoku playing field
def filter_lines(image, lines):
    # Removes lines that are probably duplicates and returns
    # the remaining ones
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

    # Removes lines that are probably not part of the 
    # sudoku playing field and returns the remaining ones
    def keep_sudoku_lines(lines):
        lines.sort()
        sudoku_lines = lines
        rhos = []
        deviation = 1000

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
                deviation = rho_deviation_sum
                sudoku_lines = lines[i:i+10]
        
        return sudoku_lines

    vertical_lines=[]
    horizontal_lines=[]

    # Keep horizontal/vertical lines
    for line in lines:
        rho, theta = line[0]
        if ((theta > 1.52) and (theta < 1.62)):
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

# Computes the intersections of each horizontal line
# with each vertical line
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

# Extracts the fields of the sudoku in the given image
# using the given intersections as their boundaries
def extract_fields(image, intersections):
    def prune_field(field):
        pruned_field = field.copy()

        def is_done(pruned_field):
            for i in np.arange(len(pruned_field[0])):
                if pruned_field[0,i] == 255:
                    return False
                elif pruned_field[len(pruned_field)-1,i] == 255:
                    return False
            for i in np.arange(len(pruned_field)):
                if pruned_field[i,0] == 255:
                    return False
                elif pruned_field[i,len(pruned_field[0])-1] == 255:
                    return False
            return True


        while True:
            if pruned_field.shape[0] <= 2 or field.shape[1] <= 2 :
                return None
            if is_done(pruned_field):
                break
            pruned_field = pruned_field[1:len(pruned_field)-1, 1:len(pruned_field[0])-1]
                
        return pruned_field

    def erode(image):
        #result = cv2.erode(image, cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3)), iterations=1)
        result = cv2.morphologyEx(image, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3)))
        result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3)))
        n = 10
        result = cv2.copyMakeBorder(result, n, n, n, n, cv2.BORDER_CONSTANT, value=0)
        return result

    if intersections is None:
        return None

    fields = np.ndarray((9,9), np.ndarray)

    for i in np.arange(0, 9):
        for j in np.arange(0, 9):
            upper_left = intersections[i,j]
            upper_right = intersections[i,j+1]
            lower_left = intersections[i+1,j]
            lower_right = intersections[i+1,j+1]
            
            field = image[int(np.max((upper_left[1], upper_right[1]))):int(np.min((lower_left[1], lower_right[1]))), \
                int(np.max((upper_left[0], lower_left[0]))):int(np.min((upper_right[0], lower_right[0])))]

            # Noise reduction and centering
            fields[i,j] = erode(prune_field(field))

    return fields

# Encapsulates the whole process of retrieving the sudoku playing field from the given image
def extract_sudoku(image):
    # Preprocess image
    image_prep = preprocessing(image)

    # Line detection
    lines = cv2.HoughLines(image_prep, 1, np.pi/180, 260)

    # Filter Lines
    horizontal_lines, vertical_lines = filter_lines(image_prep, lines)

    # Get intersections
    intersections = get_intersections(horizontal_lines, vertical_lines)

    # Extract fields
    fields = extract_fields(image_prep, intersections)

    return fields, intersections