from tqdm import tqdm

from classes.dtos import FrameData
from classes.process import Processor


class ProgressBarProcessor(Processor):

    def __init__(self, desc: str):
        self.bar = None
        self.desc = desc

    def process(self, frame_data: FrameData, **kwargs):
        if not self.bar:
            self.bar = tqdm(desc=self.desc, total=frame_data.length)
        self.bar.update(1)
