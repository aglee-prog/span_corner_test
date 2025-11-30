import math

from classes import BaseResult
from utils.common_utils import more_than_null, vector_from_points, vector_sum, vector_to_points, angle, distance, \
    point_inside_polygon


class Result(BaseResult, ):

    def __init__(self):
        super().__init__()
        self.sequence = ''
        self.turns = []
        self.trails = []
        self.is_counting = False
        self.frames_before_turn = 0
        self.frames_in_zone = 0
        self.is_set_scale = False

    def total_count_by_fps(self, fps):
        left_turn_count = 0
        right_turn_count = 0
        for x in self.turns:
            time_to_turn = round((x[1] - x[0]) / fps, 2)
            if time_to_turn > 0.35:
                if not left_turn_count + right_turn_count == 10:
                    if x[2] == 'L':
                        left_turn_count += 1
                    if x[2] == 'R':
                        right_turn_count += 1

        return left_turn_count + right_turn_count

    def status_for_total(self, total):

        status = 'OK'

        if not total >= 10:
            status = "ERROR: total turns less than 10"

        if not self.detection_percent() > 10:
            status = "ERROR: The animal is not recognized"

        return status


class Animal:
    cords = []
    scale = 1
    base_size = 110  # globals()['global_base_size']  # 60 for mice 110 for rats

    def __init__(self, data):
        self.cords = data[0:7]

    @property
    def is_set(self) -> bool:
        return all(more_than_null(i) for i in self.cords)

    @property
    def valid(self) -> bool:
        return all(more_than_null(i) for i in self.cords[0:3]) and \
            int(distance(self.cords[3], self.cords[0])) < 60

    @property
    def center(self):
        return self.cords[0]

    @property
    def neck(self):
        return self.cords[3]

    @property
    def animal_length(self):
        result = int(distance(self.center, self.neck))
        data = self.cords[3:]
        idx = range(len(data))
        for i in idx:
            n = i + 1
            if n in idx:
                if more_than_null(data[i]) and more_than_null(data[n]):
                    result += int(distance(data[i], data[n]))
                else:
                    result = 0
                    break
        return result

    def get_scale(self):
        if self.animal_length > 0:
            scale = round(self.animal_length / self.base_size, 4)
            if scale > 1.8:
                return 1.8
            if scale < 0.6:
                return 0.6
            return scale
        else:
            return 1

    @property
    def vector(self):
        return vector_from_points(self.cords[0], self.cords[3], 20)


class Roi:
    cords = []
    l_vector = [0, 0]
    r_vector = [0, 0]
    length = 350
    offset = 150
    distance_to_start = 185  # globals()['global_distance_to_start']  # 110 for mice for rats 185

    def __init__(self, data):
        self.cords = data[7:]
        self.l_vector, self.r_vector = self.get_roi_vectors(self.cords)

    @property
    def is_set(self) -> bool:
        return all(more_than_null(i) for i in self.cords)

    @property
    def is_valid(self) -> bool:
        deg = abs(int(math.degrees(angle(self.l_vector, self.r_vector))))
        return self.is_set and 20 < deg < 50

    @property
    def bisector(self):
        return vector_sum(self.l_vector, self.r_vector)

    @property
    def center(self):
        return self.cords[0]

    @property
    def roi_cords(self):
        center, left = vector_to_points(self.center, self.l_vector)
        center, right = vector_to_points(self.center, self.r_vector)
        return [center, left, right]

    def get_roi_vectors(self, data):
        roi_vector_l = vector_from_points(data[0], data[1], self.length)
        roi_vector_r = vector_from_points(data[0], data[2], self.length)

        center, roi_left_point = vector_to_points(data[0], roi_vector_l)
        center, roi_right_point = vector_to_points(data[0], roi_vector_r)

        roi_vector_l = vector_from_points(center, roi_left_point, self.length)
        roi_vector_r = vector_from_points(center, roi_right_point, self.length)

        return [roi_vector_l, roi_vector_r]

    @property
    def with_offset(self):
        center = self.center
        roi_left_point = self.l_vector
        roi_right_point = self.r_vector
        line_length = 650

        bisector_init_point, bisector_term_point = vector_to_points(center, self.bisector)
        offset_vector = vector_from_points(bisector_init_point, bisector_term_point, -self.offset)
        _, offset_center = vector_to_points(center, offset_vector)

        _, roi_left_direction_term_point = vector_to_points(offset_center, roi_left_point)
        _, roi_right_direction_term_point = vector_to_points(offset_center, roi_right_point)

        roi_vector_l = vector_from_points(offset_center, roi_left_direction_term_point, line_length)
        roi_vector_r = vector_from_points(offset_center, roi_right_direction_term_point, line_length)

        _, roi_left_point = vector_to_points(offset_center, roi_vector_l)
        _, roi_right_point = vector_to_points(offset_center, roi_vector_r)

        return [offset_center, roi_left_point, roi_right_point]

    def get_distance(self, cords):

        if cords is not None and more_than_null(self.center) and more_than_null(cords):
            return int(distance(self.center, cords))
        else:
            return 0

    def get_distance_to_neck(self, animal: Animal):
        return self.get_distance(animal.neck)

    def get_distance_to_nose(self, animal: Animal):
        if more_than_null(self.center) and more_than_null(animal.center):
            return int(distance(self.center, animal.center))
        else:
            return 0

    def get_angle(self, animal: Animal):
        return int(math.degrees(angle(self.bisector, animal.vector)))

    def is_inside(self, animal: Animal) -> bool:
        result = False
        for p in animal.cords:
            result = point_inside_polygon(p, self.with_offset)
            if result:
                break

        return result

    def is_in_counting_zone(self, animal: Animal, scale) -> bool:
        return 0 < self.get_distance_to_neck(animal) < self.distance_to_start * scale and self.is_inside(animal)

    def is_scoring_zone_reached(self, animal: Animal, scale: int) -> bool:
        return 0 < self.get_distance_to_nose(animal) < self.distance_to_start * scale

    def can_score_turn(self, animal: Animal, scale: int) -> bool:
        return self.is_set and animal.valid and self.is_inside(animal) and self.is_in_counting_zone(animal, scale)

    def can_start_scoring(self, animal: Animal, scale: int) -> bool:
        return self.is_set and animal.is_set and self.is_inside(animal) and self.is_scoring_zone_reached(animal, scale)
