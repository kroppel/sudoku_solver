# Project sudoku_solver
## The basic idea
The aim of this project was to implement a python script which takes in an image/video,
extracts the sudoku on it if there is one, and solves it.


## Extracting the sudoku
Extracting the sudoku from the given image consists of the following steps:

1. Preprocessing the input image
2. Detecting lines on the image that describe the sudoku
3. Extracting the single number fields of the sudoku and do some more preprocessing
   before Optical Character Recognition (OCR) is done
4. OCR

![Sudoku Extraction Example Image](https://user-images.githubusercontent.com/54138402/98471230-295e2900-21eb-11eb-9a8d-4f1eb55634e1.PNG)

### 1. Preprocessing
Here I converted the given BGR input image into a greyscale one,
and used adaptive thresholding to obtain a binary image.

### 2. Detecting lines
To detect lines on the preprocessed image I used Hough Transformation.
Then I filtered all lines but those that are most likely to represent the sudoku lines.
First I filtered out duplicated lines, as it is in the nature of the hough transformation that
the maximum in hough space usually spreads out over more than one pair of line parameters.
Then I removed all lines that were neither horizontally nor vertically aligned.
Finally I iterated through the remaining horizontal and vertical lines respectively and searched for a group of ten adjacent lines
that roughly have the same pairwise distance with their direct neighbours.
The most fitting two sets of lines are returned.

### 3. Extracting the number fields
Using the detected sudoku lines, I computed the intersections for each horizontal/vertical line pair.
The intersections define the boundaries for the sudoku number fields.
For the sake of good OCR results, the extracted fields are also preprocessed.
That means they were pruned to cut away possible remains of the fields' bounding lines.
Then they were inverted, because after playing around with the OCR engines for a while I noticed
that improves the results quite a bit.

### 4. OCR
I did not want to implement an OCR engine myself, because the results would probably not be sufficient
for efficient OCR within an acceptable execution time.
So I went with tesseract OCR, which is open source, easy to install and worked well.
I also tried ocr.space, which is an OCR engine available through a web api.
I liked the idea that all the OCR workloads were processed on a server and not on the client host,
and that there was no additional software to install.
But the free usage of their api is limited and I did not want to pay for their services for this little project.


## Solving the sudoku
Sudokus are solved by tracking the states of every field in the sudoku.
The state of a sudoku field is a list of possible numbers that this field can contain.
Fields that already have a number assigned have an empty state list.
In each iteration of the solving algorithm, the sudoku states are updated with respect to the sudoku rules.
These rules are implemented in simple conditional statements, where every row, column and every 3x3 segment
is inspected and states are updated.

![Sudoku Solving Example Image](https://user-images.githubusercontent.com/54138402/98471243-38dd7200-21eb-11eb-8686-c1fe07d505aa.PNG)


## My project setup
Python: Python 3.7.4

OpenCV Version: 4.2.0.34

Tesseract OCR: tesseract v4.0.0.20181030

Python Tesseract Wrapper: pytesseract 0.3.8


## The sourcecode components
### solve_sudoku_from_image.py
This python script encapsulates the whole process of image obtaining, preprocessing, extracting the sudoku and solving it.

### detect_sudoku_hough_transform.py
The script detect_sudoku_hough_transform.py uses opencv hough transformation
to detect lines in a given image/video, filters the retrieved lines for
the lines belonging to the sudoku playing field, computes their intersection points,
and retrieves the fields.
To detect your sudoku accurately, your picture should be relatively noise-free and 
should not show a lot of heterogeneous background.
As the detection algorithm only considers vertical or horizontal lines, you have
to hold your sudoku somewhat straight for it to be detected.

### sudoku_solver.py
The script sudoku_solver.py is taking in a sudoku puzzle as a two-dimensional array and outputs its solution.
The given sudoku has to be unambiguous and solvable for now.

### ocr_tesseract.py
This script implements an interface to interact with tesseract OCR for digit recognition.

### ocr_api_client.py
This script implements an interface to interact with ocr.space for digit recognition.
