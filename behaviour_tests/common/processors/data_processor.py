from classes.data_extractors import DataExtractor
from classes.dtos import FrameData
from classes.process import Processor


def normalize_raw_data(data):
    network_data = [int(x) for x in data]
    accuracy = data[2::3]
    cords = list(zip(network_data[0::3], network_data[1::3]))
    for i in range(len(accuracy)):
        if accuracy[i] < .60:
            cords[i] = 0, 0
    return cords


class DataProcessor(Processor):
    def __init__(self, data_extractor: DataExtractor, result):
        self.data_extractor = data_extractor
        self.result = result

    def process(self, frame_data: FrameData, **kwargs):
        frame = kwargs['frame']
        frame_data.fps = kwargs['fps']
        frame_data.data = normalize_raw_data(self.data_extractor.extract(frame, frame_data.number))
