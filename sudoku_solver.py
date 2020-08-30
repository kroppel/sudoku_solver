import numpy as np

def init_pfp():
    pfp = np.zeros(shape=(9,9), dtype=list)
    for i in np.arange(9):
        for j in np.arange(9):
            # Check, if field has already an assigned value
            if (sudoku_pf[i,j] == 0):
                pfp[i,j] = [1,2,3,4,5,6,7,8,9]
            else: pfp[i,j] = []
    return pfp


def maintainance_pfp(pfp, sudoku):
    # Check row and update pfp accordingly
    def check_row(rindex, pfp_entry, sudoku):
        for digit in sudoku[rindex]:
            if digit in pfp_entry: 
                pfp_entry.remove(digit)

    # Check column and update pfp accordingly
    def check_col(cindex, pfp_entry, sudoku):
        for col in sudoku:
            digit = col[cindex]
            if digit in pfp_entry: 
                pfp_entry.remove(digit)

    # Check square and update pfp accordingly
    def check_square(rindex, cindex, pfp_entry, sudoku):
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
    for i in np.arange(9):
        for j in np.arange(9):
            if len(pfp[i,j]) > 0:
                check_row(i, pfp[i,j], sudoku)
                check_col(j, pfp[i,j], sudoku)
                check_square(i, j, pfp[i,j], sudoku)

def update_sudoku_pf(pfp, sudoku):
    is_solved = True
    for i in np.arange(9):
        for j in np.arange(9):
            if sudoku_pf[i,j] == 0:
                if len(pfp[i,j]) == 1:
                    sudoku[i,j] = pfp[i,j].pop()
                    is_solved = False
    return is_solved

sudoku_initial_pf = np.asarray(
    [[0,0,0,9,0,0,7,2,8],
    [2,7,8,0,0,3,0,1,0],
    [0,9,0,0,0,0,6,4,0],
    [0,5,0,0,6,0,2,0,0],
    [0,0,6,0,0,0,3,0,0],
    [0,1,0,0,5,0,0,0,0],
    [1,0,0,7,0,6,0,3,4],
    [0,0,0,5,0,4,0,0,0],
    [7,0,9,1,0,0,8,0,5]],
    dtype=int)

sudoku_pf = np.copy(sudoku_initial_pf)
pfp = init_pfp()

counter = 0
while True:
    counter += 1
    maintainance_pfp(pfp, sudoku_pf)
    if update_sudoku_pf(pfp, sudoku_pf):
        break

print(counter)
print(sudoku_pf)