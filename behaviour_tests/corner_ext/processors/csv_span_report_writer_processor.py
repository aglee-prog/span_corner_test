import csv
import os
from csv import writer
from os.path import exists

from behaviour_tests.corner_ext.classes.dto import Result
from classes.dtos import FrameData
from classes.process import Processor


class CsvSpanReportWriterProcessor(Processor):
    csv_file = ''
    frame_data = None
    csv_head = [
        "animal_id",
        "video_uid",
        "status",
        "video_length",
        "count_of_trails",
        "left_turns",
        "right_turns",
        "left_tendency",
        "right_tendency",
        "sequence"
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
        file_path = self.file_name.split(os.sep)
        file_path.reverse()
        video_id = file_path[1].replace('I', '')
        animal_id = ''  # file_path[4]

        sequence = ''
        turns = []
        left_turn_count = 0
        right_turn_count = 0

        trails = 0

        for x in self.result.trails:
            time_to_trail = round((x[1] - x[0]) / self.frame_data.fps, 2)
            if time_to_trail > 0.35:
                trails += 1

        for x in self.result.turns:
            time_to_turn = round(x[3] / self.frame_data.fps, 2)
            sequence += x[2]
            turns.append(time_to_turn)

        total = self.result.total_count_by_fps(self.frame_data.fps)
        row = []
        row.append(animal_id)  # enro_animal_id
        row.append(video_id)  # corner_ida_videouid
        row.append(self.result.status_for_total(total))
        row.append(round(self.frame_data.length / self.frame_data.fps, 2))
        row.append(trails)
        row.append(left_turn_count)  # corner_left_s7
        row.append(right_turn_count)  # corner_right_s7
        row.append(self.result.left_tendency_percent())
        row.append(self.result.right_tendency_percent())
        row.append(sequence)
        for x in turns:
            row.append(x)

        return row

    def process(self, frame_data: FrameData, **kwargs):
        self.frame_data = frame_data
        pass

    def create_csv(self, csv_file_name) -> None:
        csv_file = open(csv_file_name, 'w+', newline='')
        csv_writer = csv.writer(csv_file)
        for i in range(10):
            self.csv_head.append('Turn #' + str(i + 1))
        csv_writer.writerow(self.csv_head)

    def get_comment(self, status):
        if status == '!WARNING!':
            return "The video may need to have a human attention!"
        if status == '!!ERROR!!':
            return "Attention! Result is not valid!"
        return ''

    def __del__(self):
        self.append_row()
