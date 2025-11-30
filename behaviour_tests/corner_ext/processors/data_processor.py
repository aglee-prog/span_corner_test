import math

from classes.data_extractors import DataExtractor
from classes.dtos import Data, BaseResult
from classes.process import Processor
from utils.common_utils import distance, vector_from_points, vector_to_points, vector_sum, angle, more_than_null, \
    point_inside_polygon, line_intersection


class DataProcessor(Processor):
    default_data = [0] * 100
    length = 350
    offset = 200

    def __init__(self, data_extractor: DataExtractor, result: BaseResult):
        self.data_extractor = data_extractor
        self.result = result

    def process(self, data: Data, **kwargs):
        frame = kwargs['frame']
        row_data = self.data_extractor.extract(frame, data.position)
        network_data = [int(x) for x in row_data]
        cords = list(zip(network_data[0::3], network_data[1::3]))
        accuracy = row_data[2::3]

        for i in range(len(accuracy)):
            if accuracy[i] < .60:
                cords[i] = 0, 0

        self.result.frames_count = data.position
        data.mouse_data = cords[0:16]
        data.triangle_data = cords[17:]

        roi_vector_l, roi_vector_r = self.get_roi_vectors(data.triangle_data)
        center = data.triangle_data[0]

        data.is_mouse_set = self.is_mouse_set(data.mouse_data)

        data.mouse_vector = self.get_mouse_vector(data.mouse_data)
        data.bisector_vector = vector_sum(roi_vector_l, roi_vector_r)
        data.angle = self.get_angle(data.mouse_vector, data.bisector_vector)
        data.distance_to_center = self.distance_to_center(center, data.mouse_data[0])
        data.roi = self.get_roi(center, roi_vector_l, roi_vector_r)
        data.is_roi_set = self.is_roi_set(data.roi)
        data.roi_with_offset = self.get_roi_with_offset(center, data.bisector_vector, roi_vector_l, roi_vector_r)
        data.is_mouse_inside_roi = self.is_mouse_inside_roi(data)

        if self.result.scale:
            data.scale = self.result.scale
        else:
            data.scale = 1

    def distance_to_center(self, roi_center, mouse_center):
        if more_than_null(roi_center) and more_than_null(mouse_center):
            return int(distance(roi_center, mouse_center))
        else:
            return 0

    def is_roi_set(self, data):
        return all(more_than_null(i) for i in data[0:2])

    def is_mouse_set(self, data) -> bool:
        return all(more_than_null(i) for i in data[0:3])

    def is_mouse_inside_roi(self, data) -> bool:
        result = False
        for p in data.mouse_data:
            result = point_inside_polygon(p, data.roi_with_offset)
            if result:
                break

        return result

    def get_mouse_lenght(self, data) -> int:
        result = 0  # int(distance(data[0], data[3]))
        idx = range(len(data[3:10]))
        for i in idx:
            n = i + 1
            if n in idx:
                if more_than_null(data[i]) and more_than_null(data[n]):
                    result += int(distance(data[i], data[n]))
                else:
                    result = 0
                    break

        return result

    def get_mouse_vector(self, data):
        return vector_from_points(data[0], data[3], 20)

    def get_angle(self, roi_bisector_vector, mouse_vector):
        return int(math.degrees(angle(mouse_vector, roi_bisector_vector)))

    def get_roi(self, center, roi_vector_l, roi_vector_r):
        if any(not more_than_null(i) for i in [roi_vector_l, roi_vector_r, center]):
            return [[0, 0], [0, 0], [0, 0]]
        center, roi_left_point = vector_to_points(center, roi_vector_l)
        center, roi_right_point = vector_to_points(center, roi_vector_r)
        return [center, roi_left_point, roi_right_point]

    def get_roi_with_offset(self, center, bisector, roi_left_point, roi_right_point):
        line_length = self.length + self.offset + self.offset / 2

        bisector_init_point, bisector_term_point = vector_to_points(center, bisector)
        offset_vector = vector_from_points(bisector_init_point, bisector_term_point, -self.offset)
        _, offset_center = vector_to_points(center, offset_vector)

        _, roi_left_direction_term_point = vector_to_points(offset_center, roi_left_point)
        _, roi_right_direction_term_point = vector_to_points(offset_center, roi_right_point)

        roi_vector_l = vector_from_points(offset_center, roi_left_direction_term_point, line_length)
        roi_vector_r = vector_from_points(offset_center, roi_right_direction_term_point, line_length)

        _, roi_left_point = vector_to_points(offset_center, roi_vector_l)
        _, roi_right_point = vector_to_points(offset_center, roi_vector_r)

        return [offset_center, roi_left_point, roi_right_point]

    def get_roi_vectors(self, data):
        roi_vector_l = 0, 0
        roi_vector_r = 0, 0
        for i in range(5):
            vector_l = vector_from_points(data[0], data[1 + i], self.length)
            vector_r = vector_from_points(data[0], data[6 + i], self.length)
            roi_angle = int(math.degrees(angle(vector_r, vector_l)))
            if 18 < roi_angle < 50:
                roi_vector_l = vector_sum(roi_vector_l, vector_l)
                roi_vector_r = vector_sum(roi_vector_r, vector_r)

        if not more_than_null(roi_vector_l) or not more_than_null(roi_vector_r):
            return [[0, 0], [0, 0]]

        center, roi_left_point = vector_to_points(data[0], roi_vector_l)
        center, roi_right_point = vector_to_points(data[0], roi_vector_r)

        roi_vector_l = vector_from_points(center, roi_left_point, self.length)
        roi_vector_r = vector_from_points(center, roi_right_point, self.length)

        return [roi_vector_l, roi_vector_r]

    def get_screen_intersection(self, line1):
        r_line = line_intersection(line1, [[0, 360], [640, 360]])
        if r_line[0] < 0:
            r_line = line_intersection(line1, [[0, 0], [0, 360]])
        if r_line[0] > 640:
            r_line = line_intersection(line1, [[640, 0], [640, 360]])
        return r_line
