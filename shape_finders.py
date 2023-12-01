import cv2
import numpy as np

COLOR_BOUNDS = {
    "blue": (np.array([90, 100, 100]), np.array([150, 255, 255])),
    "red": (np.array([0, 100, 100]), np.array([25, 255, 255])),
    "green": (np.array([50, 100, 100]), np.array([80, 255, 255])),
    "yellow": (np.array([20, 100, 100]), np.array([40, 255, 255])),
} # FIX THESE LATER THEY ARE Maybe CORRECT


def find_triangles(image, color):
    image = cv2.GaussianBlur(image, (5, 5), 0)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_bound, upper_bound = COLOR_BOUNDS[color]
    
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.imshow('mask', mask)
    centers = []

    for contour in contours:
        approx = cv2.approxPolyDP(contour, 5, True)
        area = cv2.contourArea(contour)
        
        if len(approx) == 3 and area > 1000:
            x_coord = sum([item[0][0] for item in approx]) // len(approx)
            y_coord = sum([item[0][1] for item in approx]) // len(approx)

            centers.append( (x_coord, y_coord) )

    return centers

def find_squares(image, target_color, color_tolerance=100):
    # finding contours (edges of shapes) in image
    edges = cv2.Canny(image, 30, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    centers = []

    for contour in contours:
        approx = cv2.approxPolyDP(contour, 3, True)

        if len(approx) == 4:
            x_coord = sum([item[0][0] for item in approx]) // len(approx)
            y_coord = sum([item[0][1] for item in approx]) // len(approx)

            if color_distance(color_at(image, (x_coord, y_coord)), target_color) < color_tolerance:
                centers.append( (x_coord, y_coord) )

    return centers

def find_circles(image, target_color, color_tolerance=100):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    gray = cv2.GaussianBlur(gray, (9, 9), 2)
    
    # Use the Hough Circle Transform to detect circles
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=20,
        param1=50,
        param2=30,
        minRadius=50,
        maxRadius=200 # Might want to tweak these values for real data
    )

    centers = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            center = (circle[0], circle[1])
            if color_distance(color_at(image, center), target_color) < color_tolerance:
                centers.append(center)
    return centers

def find_octagons(image, target_color, color_tolerance=100):
        # finding contours (edges of shapes) in image
    edges = cv2.Canny(image, 30, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    centers = []
    circle_centers = find_circles(image, target_color, color_tolerance=color_tolerance)[1]

    for contour in contours:
        approx = cv2.approxPolyDP(contour, 3, True)

        if len(approx) >= 8:
            x_coord = sum([item[0][0] for item in approx]) // len(approx)
            y_coord = sum([item[0][1] for item in approx]) // len(approx)

            # Check if it's too close to a circle
            if (not circle_centers or min([(circle_x - x_coord)**2 + (circle_y - y_coord)**2 for (circle_x, circle_y) in circle_centers]) >= 100) and color_distance(color_at(image, (x_coord, y_coord)), target_color) < color_tolerance:
                centers.append( (x_coord, y_coord) )

    return centers

# Helpers because I'm that cool
def color_at(image, coordinate):
    # Why is it backword? Good question
    return image[coordinate[1]][coordinate[0]]

def color_distance(col1, col2):
    return (col1[0] - col2[0]) ** 2 + (col1[1] - col2[1]) ** 2 + (col1[2] - col2[2]) ** 2
