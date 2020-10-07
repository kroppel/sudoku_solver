# sudoku_solver
The script sudoku_solver.py taking in a sudoku puzzle as a two-dimensional array and outputs its solution.
The given sudoku has to be unambiguous and solvable for now.

The script detect_sudoku_hough_transform.py uses opencv hough transformation
to detect lines in a given image/video, filters the retrieved lines for
the lines belonging to the sudoku playing field, computes their intersection points,
and retrieves the fields.
To detect your sudoku accurately, your picture should be relatively noise-free and 
should not show a lot of heterogeneous background.
As the detection algorithm only considers vertical or horizontal lines, you have
to hold your sudoku somewhat straight for it to be detected.
