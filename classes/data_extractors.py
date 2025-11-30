from abc import ABC, abstractmethod

import pandas as pd
from dlclive import Processor as DLCProcessor, DLCLive


class DataExtractor(ABC):
    default_data = [0] * 100

    @abstractmethod
    def extract(self, frame, position):
        pass


class H5DataExtractor(DataExtractor):

    def __init__(self, dataset_file):
        self.df = pd.read_hdf(dataset_file)

    def extract(self, frame, position):
        if position in self.df.index:
            data = self.df.iloc[position].to_numpy()
        else:
            data = self.default_data

        return data


class DLCLiveDataExtractor(DataExtractor):
    initialized = False

    def __init__(self, model):
        self.dlc_processor = DLCProcessor()
        self.dlc_live = DLCLive(model, processor=self.dlc_processor)

    def extract(self, frame, position):
        if not frame.any():
            return self.default_data

        if not self.initialized:
            self.dlc_live.init_inference(frame)
            self.initialized = True
        r = []
        data = self.dlc_live.get_pose(frame)
        for d in data:
            r.append(int(d[0]))
            r.append(int(d[1]))
            r.append(d[2])

        return r
