import cv2
import numpy as np
from PIL import ImageFont, Image, ImageDraw

fontC = ImageFont.truetype("./license_plate/font/platech.ttf", 14, 0)


def draw_rect_box(image, rect, add_text):
    cv2.rectangle(image, (int(rect[0]), int(rect[1])), (int(rect[0] + rect[2]), int(rect[1] + rect[3])), (0, 0, 255), 2,
                  cv2.LINE_AA)
    cv2.rectangle(image, (int(rect[0] - 1), int(rect[1]) - 16), (int(rect[0] + 150), int(rect[1])), (0, 0, 255), -1,
                  cv2.LINE_AA)

    img = Image.fromarray(image)
    draw = ImageDraw.Draw(img)
    # draw.text((int(rect[0]+1), int(rect[1]-16)), addText.decode("utf-8"), (255, 255, 255), font=fontC)
    draw.text((int(rect[0] + 1), int(rect[1] - 16)), add_text, (255, 255, 255), font=fontC)
    imagex = np.array(img)

    return imagex


def resize_array(array_in, shape=None):
    if shape is None:
        return array_in
    m, n = shape
    k1, k2 = array_in.shape

    if m == k1 and n == k2:
        return array_in
    else:
        y = np.zeros((m, n), dtype=type(array_in[0, 0]))

        # k = len(array_in)
        p, q = k1 / m, k2 / n
        for i in range(m):
            y[i, :] = array_in[np.int_(i * p), np.int_(np.arange(n) * q)]
        return y
