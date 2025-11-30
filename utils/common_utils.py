import math
import os
from math import atan2

import click
import cv2
import numpy as np


def vector_from_points(initial, direction, length):
    initial = np.array(initial, dtype=float)
    direction = np.array(direction, dtype=float)

    vector = direction - initial
    magnitude = np.linalg.norm(vector)

    epsilon = 1e-10
    if magnitude > epsilon:
        normalized_vector = vector / magnitude * length
        return int(normalized_vector[0]), int(normalized_vector[1])

    return 0, 0


def vector_sum(vector_a, vector_b):
    result = np.array(vector_a, dtype=float) + np.array(vector_b, dtype=float)
    return int(result[0]), int(result[1])


def vector_to_points(initial, terminal):
    xi, yi = initial
    xt, yt = terminal
    return [[int(xi), int(yi)], [int(xi + xt), int(yi + yt)]]


def distance(v1, v2):
    return math.sqrt(sum((b - a) ** 2 for a, b in zip(v1, v2)))


def angle(v1, v2):
    rads = atan2(v2[1], v2[0]) - atan2(v1[1], v1[0])
    if rads > np.pi:
        return rads - np.pi * 2
    if rads < -np.pi:
        return rads + np.pi * 2
    return rads


def more_than_null(p):
    return p[0] > 0 and p[1] > 0


def point_inside_polygon(point, poly, include_edges=True):
    x, y = point
    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if p1y == p2y:
            if y == p1y:
                if min(p1x, p2x) <= x <= max(p1x, p2x):
                    inside = include_edges
                    break
                elif x < min(p1x, p2x):
                    inside = not inside
        else:
            if min(p1y, p2y) <= y <= max(p1y, p2y):
                xinters = (y - p1y) * (p2x - p1x) / float(p2y - p1y) + p1x
                if x == xinters:
                    inside = include_edges
                    break
                if x < xinters:
                    inside = not inside

        p1x, p1y = p2x, p2y

    return inside


def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return int(x), int(y)


def triangle_sqr(p1, p2, p3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    return abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0


def is_point_in_boundaries(current: [int, int], boundary_center: [int, int], offset: int) -> bool:
    x, y = boundary_center
    x2, y2 = current
    return (x - offset < x2 < x + offset) and (y - offset < y2 < y + offset) and x2 > 0 and y2 > 0


def get_files_or_fail(files_path):
    files = get_mp4_files(files_path)
    if not len(files) > 0:
        click.secho('There are no mp4 files in ' + files_path, fg='red')
        exit()
    return files


def get_mp4_files(dir_name):
    _files = os.listdir(dir_name)
    files = []
    for idx, file in enumerate(_files):
        read_path = os.path.join(dir_name, file)
        if (os.path.isfile(read_path) and file.endswith('.mp4') or file.endswith('.MP4')) and not file.endswith(
                'output.mp4'):
            if file.endswith('.MP4'):
                new_file = read_path.replace('.MP4', '.mp4')
                os.rename(read_path, new_file)
                read_path = new_file
            files.append(read_path)
        if os.path.isdir(read_path):
            files.extend(get_mp4_files(read_path))
    return files


def to_gray_scale(frame):
    return cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)


def add_border(frame):
    return cv2.copyMakeBorder(frame, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=[0, 0, 0])


def resize_image(image, width, height, COLOUR=[0, 0, 0]):
    h, w, layers = image.shape
    if h > height:
        ratio = height / h
        image = cv2.resize(image, (int(image.shape[1] * ratio), int(image.shape[0] * ratio)))
    h, w, layers = image.shape
    if w > width:
        ratio = width / w
        image = cv2.resize(image, (int(image.shape[1] * ratio), int(image.shape[0] * ratio)))
    h, w, layers = image.shape
    if h < height and w < width:
        hless = height / h
        wless = width / w
        if (hless < wless):
            image = cv2.resize(image, (int(image.shape[1] * hless), int(image.shape[0] * hless)))
        else:
            image = cv2.resize(image, (int(image.shape[1] * wless), int(image.shape[0] * wless)))
    h, w, layers = image.shape
    if h < height:
        df = height - h
        df /= 2
        image = cv2.copyMakeBorder(image, int(df), int(df), 0, 0, cv2.BORDER_CONSTANT, value=COLOUR)
    if w < width:
        df = width - w
        df /= 2
        image = cv2.copyMakeBorder(image, 0, 0, int(df), int(df), cv2.BORDER_CONSTANT, value=COLOUR)
    image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    return image
