from classes.dtos import FrameData
from classes.process import Processor
from behaviour_tests.corner_ext.classes.dto import Animal, Roi, Result


class TendencyProcessor(Processor):
    def __init__(self, result: Result):
        self.result = result

    def process(self, frame_data: FrameData, **kwargs):
        animal = Animal(frame_data.data)
        roi = Roi(frame_data.data)
        angle = roi.get_angle(animal)
        if animal.is_set and roi.is_set and roi.is_in_counting_zone(animal, self.result.scale):
            if -45 > angle > -90:
                self.result.left_tendency_frames += 1
            if 45 < angle < 90:
                self.result.right_tendency_frames += 1
