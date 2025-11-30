import cv2

from classes import FrameData
from classes.process import Processor


class WatermarkProcessor(Processor):

    def __init__(self, path):
        self.wm = cv2.imread(path)
        self.h_wm, self.w_wm = self.wm.shape[:2]

    def process(self, _: FrameData, **kwargs):
        frame = kwargs['frame']
        if not frame.any():
            pass

        if self.wm is None:
            pass

        self.add_watermark(frame)

    def add_watermark(self, frame):
        h_img, w_img = frame.shape[:2]
        center_x = int(w_img / 2)
        center_y = int(h_img / 2)
        top_y = center_y - int(self.h_wm / 2)
        left_x = center_x - int(self.w_wm / 2)
        bottom_y = top_y + self.h_wm
        right_x = left_x + self.w_wm
        roi = frame[top_y:bottom_y, left_x:right_x]
        result = cv2.addWeighted(roi, 1, self.wm, 0.05, 0)
        frame[top_y:bottom_y, left_x:right_x] = result
        return frame
