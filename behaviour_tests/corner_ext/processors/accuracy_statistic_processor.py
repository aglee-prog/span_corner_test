import math

from behaviour_tests.corner_ext.classes.dto import Animal, Roi, Result
from classes.dtos import FrameData
from classes.process import Processor
from utils.common_utils import distance, vector_from_points, angle, more_than_null


class AccuracyStatisticProcessor(Processor):
    def __init__(self, result: Result):
        self.result = result

    def process(self, frame_data: FrameData, **kwargs):
        animal = Animal(frame_data.data)
        roi = Roi(frame_data.data)
        self.result.corrupted = False
        self.result.frames_count += 1

        if animal.is_set and roi.is_set:
            self.result.detected_frames += 1
            valid_roi = self.is_roi_valid(roi.cords)
            valid_pose = self.is_pose_valid(animal.cords)
            self.result.corrupted = not valid_roi or not valid_pose
            if self.result.corrupted:
                self.result.corrupted_frames_count += 1

    def is_pose_valid(self, data):
        result = True
        idx = range(len(data[0:5]))
        for i in idx:
            n = i + 1
            if n in idx and int(distance(data[i], data[n])) > 80:
                result = False
                break

        # distance between left and right ear
        if not 10 < int(distance(data[1], data[2])) < 80:
            result = False

        # distance between nose and neck
        if not 5 < int(distance(data[0], data[3])) < 80:
            result = False

        return result

    def is_roi_valid(self, data):
        if not all(not more_than_null(i) for i in data):
            return False

        vector_l = vector_from_points(data[0], data[1], 320)
        vector_r = vector_from_points(data[0], data[2], 320)
        roi_angle = int(math.degrees(angle(vector_r, vector_l)))
        return 18 < roi_angle < 50
