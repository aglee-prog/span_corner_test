import csv
from csv import writer
from os.path import exists

from behaviour_tests.corner_ext.classes.dto import Result
from classes.dtos import FrameData
from classes.process import Processor


class CsvWriterProcessor(Processor):
    csv_file = ''
    csv_head = [
        "File",
        "Trails",
        "Left turns",
        "Right turns",
        "Left tendency",
        "Right tendency",
        "Detection percent",
        "Satus"
    ]

    def __init__(self, csv_file, file_name, result: Result):
        if not exists(csv_file):
            self.create_csv(csv_file)
        self.csv_file = csv_file
        self.result = result
        self.file_name = file_name

    def append_row(self):
        with open(self.csv_file, 'a+', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(self.get_row())

    def get_row(self):
        row = []
        row.append(self.file_name)
        row.append(len(self.result.trails))
        row.append(self.result.left_turn_count)
        row.append(self.result.right_turn_count)
        row.append(self.result.left_tendency_percent())
        row.append(self.result.right_tendency_percent())
        row.append(self.result.detection_percent())
        row.append(self.result.status())
        return row

    def process(self, frame_data: FrameData, **kwargs):
        pass

    def create_csv(self, csv_file_name) -> None:
        csv_file = open(csv_file_name, 'w+', newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(self.csv_head)

    def __del__(self):
        self.append_row()
