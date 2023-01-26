from numpy import cos, sin, copy, min, pi, arange, asarray, mean, abs, max, sum, ndarray
from cv2 import cvtColor, COLOR_BGR2GRAY, adaptiveThreshold, ADAPTIVE_THRESH_MEAN_C, THRESH_BINARY_INV, line, circle, \
     HoughLines, morphologyEx, MORPH_OPEN, getStructuringElement, MORPH_ELLIPSE, MORPH_CLOSE, erode, copyMakeBorder, BORDER_CONSTANT, \
    threshold

# Preprocesses the given image, returning a binary representation of it
def preprocessing(image):
    image_gray =cvtColor(image,COLOR_BGR2GRAY)
    image_threshold = adaptiveThreshold(src=image_gray, maxValue=255, \
        adaptiveMethod = ADAPTIVE_THRESH_MEAN_C, thresholdType = THRESH_BINARY_INV, blockSize=15, C=6)
    
    return image_threshold

# Draws the given lines onto a copy of the given image
# and returns it
def draw_lines(image, lines):
    image_lines = copy(image)

    for dline in lines:
        rho,theta = dline
        a = cos(theta)
        b = sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        line(image_lines,(x1,y1),(x2,y2),(0,0,255),2)

    return image_lines

# Draws the given points onto a copy of the given image
# and returns it
def draw_points(image, points):
    if points is None:
        return image

    image_points = copy(image)

    for line in points:
        for point in line:
            circle(image_points, point, 3, (0, 255, 0), 5)

    return image_points

def extract_about_n_lines(image, iterations = 1):
    # Parameters for setting an interval, in which the number of retrieved lines has to lie
    n = 100
    max_deviation = 20

    lines = []
    votes_upper_bound = min(image.shape)
    votes_lower_bound = 0
    min_votes = int((votes_upper_bound + votes_lower_bound)/3)

    while (iterations > 0):
        extracted_lines = HoughLines(image, 1, pi/180, min_votes)

        if not extracted_lines is None:
            lines = extracted_lines
        if len(lines) > n + max_deviation:
            votes_lower_bound = min_votes
            min_votes = int((votes_upper_bound + votes_lower_bound)/2)
        elif len(lines) < n - max_deviation:
            votes_upper_bound = min_votes
            min_votes = int((votes_upper_bound + votes_lower_bound)/2)
        iterations -= 1

    return lines

# Filters out irrelevant lines, returning the ten lines
# that belong to the sudoku playing field
def filter_lines(lines):
    # Removes lines that are neither horizontally nor vertically aligned
    def get_horizontal_and_vertical_lines(lines):
        vertical_lines=[]
        horizontal_lines=[]

        for line in lines:
            rho, theta = line[0]
            if ((theta > 1.5407) and (theta < 1.6007)):
                horizontal_lines.append((rho, theta))
            elif ((theta > -0.05) and (theta < 0.05)):      
                vertical_lines.append((rho, theta))

        return horizontal_lines, vertical_lines


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
        rho_deviation_sum = 0

        # Parameter for maximal value of the rho devation sum for the processed set of lines to be counted as sudoku lines
        deviation_max = 15

        for line in lines:
            rho, theta = line
            rhos.append(rho)

        for i in arange(0, len(lines)-9):
            rho_candidates = rhos[i:i+10]
            rho_diffs = asarray(rho_candidates[1:10]) - asarray(rho_candidates[0:9])
            rho_diff_mean = int(mean(rho_diffs))
            rho_abs_deviations = abs(rho_diffs - rho_diff_mean)
            max_single_deviation = max(rho_abs_deviations) 
            rho_deviation_sum = sum(rho_abs_deviations)

            if deviation > rho_deviation_sum:
                deviation = rho_deviation_sum
                sudoku_lines = lines[i:i+10]
        
        if deviation > deviation_max:
            return []

        return sudoku_lines

    # Keep horizontal/vertical lines
    horizontal_lines, vertical_lines = get_horizontal_and_vertical_lines(lines)

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

    intersections = ndarray((10,10), tuple)

    for i in arange(0, 10):
        h_line = h_lines[i]
        for j in arange(0, 10):
            v_line = v_lines[j]
            h_rho, h_theta = h_line
            v_rho, v_theta = v_line
            x_i, y_i = 0, 0

            if (v_theta == 0):
                x_i = v_rho
            else:
                x_i = ((h_rho * sin(v_theta)) - (v_rho * sin(h_theta))) / \
                    ((cos(h_theta) * sin(v_theta)) - (cos(v_theta) * sin(h_theta)))
            y_i = ((h_rho / sin(h_theta)) - (x_i * (cos(h_theta) / sin(h_theta))))
            
            intersections[i,j] = (x_i, y_i)

    return intersections

# Extracts the fields of the sudoku in the given image
# using the given intersections as their boundaries
def extract_fields(image, intersections):
    additional_prune = 5
    def prune_field(field):
        pruned_field = field.copy()
        pruning_mask = field==255

        row_mask = sum(pruning_mask, axis=1)==pruned_field.shape[1]
        col_mask = sum(pruning_mask, axis=0)==pruned_field.shape[0]

        row_min, col_min = 0, 0
        row_max, col_max = pruned_field.shape[0], pruned_field.shape[1]

        for i in arange(pruned_field.shape[0]):
            if row_mask[i] == 0:
                row_min = i
                break
        for i in arange(pruned_field.shape[1]):
            if col_mask[i] == 0:
                col_min = i
                break
        for i in arange(1, pruned_field.shape[0]+1):
            if row_mask[-i] == 0:
                row_max = -i+1
                break
        for i in arange(1, pruned_field.shape[1]+1):
            if col_mask[-i] == 0:
                col_max = -i+1

        # return unpruned image if no number in it
        if row_min >= row_max or col_min >= col_max:
            return pruned_field[additional_prune:-additional_prune+1,additional_prune:-additional_prune+1]



        """def is_done(pruned_field, pruning_mask):
            for i in arange(len(pruned_field[0])):
                if pruned_field[0,i] == 255:
                    return False
                elif pruned_field[len(pruned_field)-1,i] == 255:
                    return False
            for i in arange(len(pruned_field)):
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
            pruned_field = pruned_field[1:len(pruned_field)-1, 1:len(pruned_field[0])-1]"""
      
    
        pruned_field = pruned_field[row_min+additional_prune:row_max-additional_prune, col_min+additional_prune:col_max-additional_prune]
        
        return pruned_field

    def morphology(image):
        result = morphologyEx(image, MORPH_OPEN, getStructuringElement(MORPH_ELLIPSE,(3,3)))
        result = morphologyEx(result, MORPH_CLOSE, getStructuringElement(MORPH_ELLIPSE,(3,3)))
        result = erode(result, (3,3))
        n = 10
        result = copyMakeBorder(result, n, n, n, n, BORDER_CONSTANT, value=0)
        return result

    if intersections is None:
        return None, False

    fields = ndarray((9,9), ndarray)

    for i in arange(0, 9):
        for j in arange(0, 9):
            upper_left = intersections[i,j]
            upper_right = intersections[i,j+1]
            lower_left = intersections[i+1,j]
            lower_right = intersections[i+1,j+1]
            
            field = image[int(max((upper_left[1], upper_right[1]))):int(min((lower_left[1], lower_right[1]))), \
                int(max((upper_left[0], lower_left[0]))):int(min((upper_right[0], lower_right[0])))]

            # Noise reduction and centering
            #_, fields[i,j] = threshold(morphology(prune_field(field)), 127, 255, THRESH_BINARY_INV)

            _, fields[i,j] = threshold(prune_field(field), 127, 255, THRESH_BINARY_INV)

    return fields, True

# Encapsulates the whole process of retrieving the sudoku playing field from the given image
def extract_sudoku(image):
    # Preprocess image
    image_prep = preprocessing(image)

    # Line detection
    lines = extract_about_n_lines(image_prep)
    
    # Filter Lines
    horizontal_lines, vertical_lines = filter_lines(lines)

    # Get intersections
    intersections = get_intersections(horizontal_lines, vertical_lines)

    # Extract fields
    fields, ret_val = extract_fields(image_prep, intersections)

    return fields, intersections, horizontal_lines, vertical_lines
