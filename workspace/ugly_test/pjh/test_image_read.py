import unittest
import cv2
import numpy as np
import matplotlib.pyplot as plt


def make_coordinates(image, line_parameters):
    slope, intercept = line_parameters
    y1 = image.shape[0]
    y2 = int(y1*(3/5))
    x1 = int((y1 - intercept)/slope)
    x2 = int((y2 - intercept)/slope)
    return np.array([x1, y1, x2, y2])


def average_slope_intercept(image, lines):
    left_fit, right_fit = [], []
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        parameters = np.polyfit((x1, x2), (y1, y2), 1)
        # print(parameters)
        slope = parameters[0]
        intercept = parameters[1]
        if slope < 0:
            left_fit.append((slope, intercept))
        else:
            right_fit.append((slope, intercept))
    # print(left_fit)
    # print(right_fit)
    if left_fit and right_fit:
        left_fit_average = np.average(left_fit, axis=0)
        right_fit_average = np.average(right_fit, axis=0)
        left_line = make_coordinates(image, left_fit_average)
        right_line = make_coordinates(image, right_fit_average)
        return np.array([left_line, right_line])
    else:
        return None


def canny(image):
    # gray scaling
    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # blur treatment
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    # apply canny method
    canny_image = cv2.Canny(blurred_image, 50, 150)
    return canny_image


def region_of_interest(image):
    # specify the region we are interested in -> triangular
    height = image.shape[0]  # row value
    # width = image.shape[1]  # column value
    polygons = np.array([
        [(200, height), (1100, height), (550, 250)]
    ])
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, polygons, 255)
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image


def display_lines(image, lines):
    line_image = np.zeros_like(image)
    if lines is not None:
        for x1, y1, x2, y2 in lines:
            # print(line)
            cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 10)
    return line_image


class MyTestCase(unittest.TestCase):
    def test_line_recognition_image(self):
        image = cv2.imread('test_image.jpg')
        lane_image = np.copy(image)
        canny_image = canny(lane_image)
        cropped_image = region_of_interest(canny_image)
        lines = cv2.HoughLinesP(
            cropped_image, 2, np.pi / 180, 100, np.array([]), minLineLength=40, maxLineGap=5)
        averaged_lines = average_slope_intercept(lane_image, lines)
        line_image = display_lines(lane_image, averaged_lines)
        combined_image = cv2.addWeighted(lane_image, 0.8, line_image, 1, 1)

        # plt.imshow(canny_image)
        # plt.show()

        cv2.imshow('image', combined_image)
        cv2.waitKey(0)

    def test_line_recognition_video(self):
        cap = cv2.VideoCapture("test2.mp4")
        while cap.isOpened():
            _, frame = cap.read()
            canny_image = canny(frame)
            cropped_image = region_of_interest(canny_image)
            lines = cv2.HoughLinesP(
                cropped_image, 2, np.pi / 180, 100, np.array([]), minLineLength=40, maxLineGap=5)
            averaged_lines = average_slope_intercept(frame, lines)
            line_image = display_lines(frame, averaged_lines)
            combined_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)

            # plt.imshow(canny_image)
            # plt.show()

            # print image
            cv2.imshow('result', combined_image)
            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    unittest.main()
