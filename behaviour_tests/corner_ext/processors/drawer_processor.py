import cv2

from behaviour_tests.common import COLOR_BLUE, COLOR_GREEN, COLOR_GREY, COLOR_RED
from behaviour_tests.corner_ext.classes.dto import Animal, Roi, Result
from classes.dtos import FrameData
from classes.process import Processor
from utils.common_utils import vector_to_points, more_than_null


class DrawerProcessor(Processor):
    status_text = []
    points = []

    pink = (100, 128, 128, 128)
    grey = (100, 128, 128, 128)
    black = (50, 50, 50, 128)
    green = (100, 255, 0, 80)
    red = (0, 0, 255, 128)

    font = cv2.FONT_HERSHEY_SIMPLEX

    def __init__(self, frame_name, result: Result, show_window=True):
        self.frame_name = frame_name
        self.result = result
        self.show_window = show_window

    def process(self, frame_data: FrameData, **kwargs):
        frame = kwargs['frame']
        if not frame.any():
            pass

        animal = Animal(frame_data.data)
        roi = Roi(frame_data.data)

        for p in frame_data.data:
            cv2.circle(frame, p, 1, COLOR_RED, 1)

        self.status_text = []
        self.draw_hub(frame, animal, roi, frame_data.number)
        self.draw_mouse_head(frame, animal)
        self.draw_mouse_body(frame, animal)
        self.draw_point(frame, animal)
        self.draw_bisector(frame, roi)
        self.draw_counting_zone(frame, roi)
        self.draw_roi(frame, roi)

        if self.show_window:
            self.show_frame(frame)

    def draw_mouse_head(self, frame, animal: Animal):
        head = animal.cords[0:4]
        points = [(head[0], head[1]), (head[0], head[2]), (head[1], head[3]), (head[2], head[3])]
        for point in points:
            if more_than_null(point[0]) and more_than_null(point[1]):
                cv2.line(frame, point[0], point[1], COLOR_BLUE, 1)

    def draw_point(self, frame, animal: Animal):
        for p in animal.cords:
            cv2.circle(frame, p, 2, COLOR_GREEN, 1)

    def draw_mouse_body(self, frame, animal):
        body = animal.cords[3:]
        for idx, val in enumerate(body):
            if len(body) > (idx + 1) and more_than_null(body[idx]) and more_than_null(body[idx + 1]):
                cv2.line(frame, body[idx], body[idx + 1], COLOR_BLUE, 1)

    def draw_roi(self, frame, roi: Roi):
        data = roi.roi_cords
        if roi.is_set:
            cv2.line(frame, data[0], data[1], self.pink, 1)
            cv2.line(frame, data[0], data[2], self.pink, 1)
            cv2.line(frame, data[1], data[2], self.pink, 1)
            cv2.circle(frame, data[0], 1, self.red, thickness=5)

    def draw_roi_offset(self, frame, roi: Roi):
        data = roi.with_offset
        if more_than_null(data[0]) and more_than_null(data[1]) and more_than_null(data[2]):
            cv2.line(frame, data[0], data[1], self.green, 1)
            cv2.line(frame, data[0], data[2], self.green, 1)
            cv2.line(frame, data[1], data[2], self.green, 1)

    def draw_status_text(self, frame):
        for c, text in enumerate(self.status_text):
            cv2.putText(frame, text, (20, 20 * (c + 1)), self.font, .6, self.green, 2)

    def draw_hub(self, frame, animal: Animal, roi: Roi, frame_pos):
        left_count = str(self.result.left_turn_count)
        right_count = str(self.result.right_turn_count)

        t_left = str(self.result.left_tendency_percent())
        t_right = str(self.result.right_tendency_percent())

        distance_to_center = str(roi.get_distance_to_neck(animal))
        angle = str(roi.get_angle(animal))
        frame_pos = str(frame_pos)

        cv2.putText(frame, "L:" + left_count + " R:" + right_count, (20, 30), self.font, .65, self.green, 2)
        cv2.putText(frame, "Tendency: " + t_left + " | " + t_right, (20, 60), self.font, .5, self.black, 1)
        cv2.putText(frame, "Distance: " + distance_to_center + "px", (20, 85), self.font, .5, self.black, 1)
        cv2.putText(frame, "Angle: " + angle, (20, 105), self.font, .5, self.black, 1)
        cv2.putText(frame, "Frame: " + frame_pos, (20, 125), self.font, .5, self.black, 1)
        cv2.putText(frame, "State: " + self.result.state_name, (20, 145), self.font, .5, self.black, 1)
        cv2.putText(frame, "Scale: " + str(self.result.scale), (20, 165), self.font, .5, self.black, 1)

    def draw_counting_zone(self, frame, roi: Roi):
        if not roi.is_set or not self.result.scale:
            return True

        if not self.result.is_counting:
            cv2.circle(frame, roi.center, round(roi.distance_to_start * self.result.scale), COLOR_BLUE, 1)

    def draw_bisector(self, frame, roi: Roi):
        if roi.is_set:
            center_point, bisector_point = vector_to_points(roi.center, roi.bisector)
            cv2.line(frame, center_point, bisector_point, COLOR_GREY, 1)

    def show_frame(self, frame):
        cv2.putText(frame, "Press Q for exit", (20, 340), self.font, .5, self.black, 1)
        cv2.imshow(self.frame_name, frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            quit()
