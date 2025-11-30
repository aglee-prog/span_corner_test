from behaviour_tests.corner_ext.classes.dto import Roi
from classes.dtos import FrameData
from classes.process import Processor
from utils.common_utils import distance, more_than_null


class CordsCacheProcessor(Processor):
    center = (0, 0)
    left = (0, 0)
    right = (0, 0)

    cords = [(0, 0), (0, 0), (0, 0)]

    def process(self, frame_data: FrameData, **kwargs):
        if not more_than_null(frame_data.data[7]):
            frame_data.data[7] = (0, 0)
            frame_data.data[8] = (0, 0)
            frame_data.data[9] = (0, 0)

        cords = frame_data.data[7:]
        center = cords[0]
        left = cords[1]
        right = cords[2]

        roi = Roi(frame_data.data)

        if roi.is_valid and distance(self.center, center) > 5:
            self.center = center

        if roi.is_valid and distance(self.left, left) > 5:
            self.left = left

        if roi.is_valid and distance(self.right, right) > 5:
            self.right = right

        if more_than_null(center) and (more_than_null(left) or more_than_null(right)):
            frame_data.data[7] = self.center
            frame_data.data[8] = self.left
            frame_data.data[9] = self.right
