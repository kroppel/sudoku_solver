from numpy import arange, asarray, zeros, copy

"""
In this script a sudoku puzzle is represented as a 
9 by 9 array called sudoku_pf, each field containing it's corresponding number,
or 0 if the number hasn't been determined yet.
A second array, called pfp, is maintained to hold a list of the possible numbers
for each field, which is empty if the number is already determined.

"""

# Initializes a new pfp for the given sudoku
def init_pfp(sudoku):
    pfp = zeros(shape=(9,9), dtype=list)
    for i in arange(9):
        for j in arange(9):
            # Check, if field has already an assigned value
            if (sudoku[i,j] == 0):
                pfp[i,j] = [1,2,3,4,5,6,7,8,9]
            else: 
                pfp[i,j] = []                
    return pfp

# Maintains the given pfp with respect to the entries of the given sudoku
def maintainance_pfp(pfp, sudoku):
    # Check row and update pfp accordingly
    def maintain_row(rindex, pfp_entry, sudoku):
        for digit in sudoku[rindex]:
            if digit in pfp_entry: 
                pfp_entry.remove(digit)

    # Check column and update pfp accordingly
    def maintain_col(cindex, pfp_entry, sudoku):
        for digit in sudoku[:,cindex]:
            if digit in pfp_entry: 
                pfp_entry.remove(digit)

    # Check square and update pfp accordingly
    def maintain_square(rindex, cindex, pfp_entry, sudoku):
        # Square index ranges
        I = [0, 1, 2]
        II = [3, 4, 5]

        if rindex in I:
            if cindex in I:
                for row in sudoku[0:3, 0:3]:
                    for digit in row:
                        if digit in pfp_entry:
                            pfp_entry.remove(digit)
            elif cindex in II:
                for row in sudoku[0:3, 3:6]:
                    for digit in row:
                        if digit in pfp_entry: 
                            pfp_entry.remove(digit)
            else: 
                for row in sudoku[0:3, 6:9]:
                    for digit in row:
                        if digit in pfp_entry: 
                            pfp_entry.remove(digit)
        elif rindex in II:
            if cindex in I:
                for row in sudoku[3:6, 0:3]:
                    for digit in row:
                        if digit in pfp_entry: 
                            pfp_entry.remove(digit)
            elif cindex in II:
                for row in sudoku[3:6, 3:6]:
                    for digit in row:
                        if digit in pfp_entry: 
                            pfp_entry.remove(digit)
            else:
                for row in sudoku[3:6, 6:9]:
                    for digit in row:
                        if digit in pfp_entry: 
                            pfp_entry.remove(digit)
        else:
            if cindex in I:
                for row in sudoku[6:9, 0:3]:
                    for digit in row:
                        if digit in pfp_entry: 
                            pfp_entry.remove(digit)
            elif cindex in II:
                for row in sudoku[6:9, 3:6]:
                    for digit in row:
                        if digit in pfp_entry: 
                            pfp_entry.remove(digit)
            else:
                for row in sudoku[6:9, 6:9]:
                    for digit in row:
                        if digit in pfp_entry: 
                            pfp_entry.remove(digit)

    # Iterate over pfp and apply above check functions
    for i in arange(9):
        for j in arange(9):
            if len(pfp[i,j]) > 1:
                maintain_row(i, pfp[i,j], sudoku)
                maintain_col(j, pfp[i,j], sudoku)
                maintain_square(i, j, pfp[i,j], sudoku)

# Check for rows, columns and squares with only one possibility for one of the numbers between 1 and 9 and fill the corresponding fields
def check_possibilities(pfp, sudoku):
    def check_prows(pfp, sudoku):
        is_solved = True
    
        for i in arange(9):
            p_hist = zeros(9)

            for j in arange(9):
                for entry in pfp[i,j]:
                    p_hist[entry-1] += 1
            
            for k in arange(1,10):
                if (p_hist[k-1] == 1):
                    for j in arange(9):
                        for entry in pfp[i,j]:
                            if (entry == k):
                                pfp[i,j] = []
                                sudoku[i,j] = k
                                maintainance_pfp(pfp, sudoku)
                                is_solved = False
        return is_solved


    def check_pcolumns(pfp, sudoku):
        is_solved = True

        for i in arange(9):
            p_hist = zeros(9)

            for j in arange(9):
                for entry in pfp[j,i]:
                    p_hist[entry-1] += 1

            for k in arange(1,10):
                if (p_hist[k-1] == 1):
                    for j in arange(9):
                        for entry in pfp[j,i]:
                            if (entry == k):
                                pfp[j,i] = []
                                sudoku[j,i] = k
                                maintainance_pfp(pfp, sudoku)
                                is_solved = False
        return is_solved

    def check_psquares(pfp, sudoku):
        is_solved = True
        offsets = [0, 3, 6]
        
        for offset_row in offsets:
            for offset_col in offsets:
                p_hist = zeros(9)
   
                for i in arange(offset_row, 3 + offset_row):
                    for j in arange(offset_col, 3 + offset_col):
                        for entry in pfp[i,j]:
                            p_hist[entry-1] += 1

                for k in arange(1,10):
                    if (p_hist[k-1] == 1):
                        for i in arange(offset_row, 3 + offset_row):
                            for j in arange(offset_col, 3 + offset_col):
                                for entry in pfp[i,j]:
                                    if (entry == k):
                                        pfp[i,j] = []
                                        sudoku[i,j] = k
                                        maintainance_pfp(pfp, sudoku)
                                        is_solved = False
        return is_solved
                                
    
    return (check_prows(pfp, sudoku) and check_pcolumns(pfp, sudoku) and check_psquares(pfp, sudoku))
    
        

# Updates the given sudoku with respect to the given pfp
def update_sudoku_pf(pfp, sudoku_pf):
    was_updated = False
    for i in arange(9):
        for j in arange(9):
            if sudoku_pf[i,j] == 0:
                if len(pfp[i,j]) == 1:
                    sudoku_pf[i,j] = pfp[i,j].pop()
                    was_updated = True
    return was_updated

def is_sudoku_solved(sudoku_pf):
    is_solved = True

    for row in sudoku_pf:
        for field in row:
            if field == 0:
                is_solved = False
                break

    return is_solved

def solve_sudoku(sudoku):
    sudoku_pf = copy(sudoku)
    pfp = init_pfp(sudoku_pf)

    counter = 0

    while True:
        print(counter)
        print(sudoku_pf)
        counter += 1
        maintainance_pfp(pfp, sudoku_pf)

        print(pfp)

        if not update_sudoku_pf(pfp, sudoku_pf) and check_possibilities(pfp, sudoku_pf):
            break

    print(counter)
    print(sudoku_pf)
    print("End")

sudoku_initial_pf = asarray(
    [[7,0,4,0,0,0,0,0,0],
    [0,0,0,3,0,0,1,7,0],
    [0,0,1,0,6,0,5,0,8],
    [0,0,0,0,3,1,0,0,2],
    [0,7,0,5,0,4,0,6,0],
    [3,0,0,8,7,0,0,0,0],
    [2,0,5,0,8,0,4,0,0],
    [0,6,3,0,0,2,0,0,0],
    [0,0,0,0,0,0,2,0,5]],
    dtype=int)

