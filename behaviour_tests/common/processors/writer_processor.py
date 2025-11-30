import cv2

from classes.dtos import FrameData
from classes.process import Processor


class WriterProcessor(Processor):
    file_output = None
    fourcc = None
    writer = None

    def __init__(self, file):
        self.fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.file_output = file.replace('.mp4', '-output.mp4')

    def process(self, data: FrameData, **kwargs):
        frame = kwargs['frame']
        fps = kwargs['fps']
        if self.writer is None:
            self.writer = cv2.VideoWriter(self.file_output, self.fourcc, fps, (640, 360))

        if not frame.any():
            pass

        self.writer.write(frame)

    def release(self):
        self.writer.release()

    def __del__(self):
        self.release()
