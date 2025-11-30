from abc import ABC, abstractmethod
from typing import List

import cv2

from classes.dtos import FrameData
from utils.common_utils import resize_image, to_gray_scale, add_border


class Processor(ABC):
    @abstractmethod
    def process(self, data: FrameData, **kwargs):
        pass


class Iterator:
    def __init__(self, file):
        self.capture = cv2.VideoCapture(file)

    def run(self):
        if not self.capture.isOpened():
            print("Error opening video stream or file")
        else:
            ctn = 0
            length = 0
            while True:
                ctn += 1
                ret, frame = self.capture.read()
                if ret:
                    position = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
                    length = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
                    fps = self.capture.get(cv2.CAP_PROP_FPS)
                    frame = resize_image(frame, 636, 356)
                    frame = to_gray_scale(frame)
                    frame = add_border(frame)
                    yield [int(position), int(length), frame, fps]

                if ctn >= length:
                    break

    def __del__(self):
        self.capture.release()
        cv2.destroyAllWindows()


class Process:
    def __init__(self, file, processors=None):
        if processors is None:
            processors = []
        self.processors = processors
        self.iterator = Iterator(file)

    def run(self):
        for position, length, frame, fps in self.iterator.run():
            data = self.process_frame(position, length, frame, fps)
            if data.is_last:
                break

    def process_frame(self, position: int, length: int, frame, fps) -> FrameData:
        data = FrameData(position, length)
        for processor in self.processors:
            processor.process(data, frame=frame, fps=fps)
        return data

    def add_processor(self, processor: Processor):
        self.processors.append(processor)

    def add_processors(self, processors: List[Processor]):
        for processor in processors:
            self.processors.append(processor)
