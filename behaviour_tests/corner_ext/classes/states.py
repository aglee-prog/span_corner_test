from behaviour_tests.corner_ext.classes.dto import Animal, Roi, Result
from classes.debouncer import Debouncer
from classes.dtos import FrameData
from classes.state_context import State
from utils.common_utils import is_point_in_boundaries


class CountingTurnsState(State):
    left_turn_threshold = -90
    right_turn_threshold = 90
    distance_to_neck = 250

    def __init__(self):
        super().__init__()
        self.frame = 0
        self.frame_start = None
        self.left_turn_debouncer = Debouncer(threshold=5)
        self.right_turn_debouncer = Debouncer(threshold=5)
        self.reset_center_debouncer = Debouncer(threshold=60)
        self.reset_mouse_debouncer = Debouncer(threshold=20)

    def process(self, frame_data: FrameData, result: Result) -> None:
        result.state_name = 'Counting Turns'

        animal = Animal(frame_data.data)
        roi = Roi(frame_data.data)
        result.is_counting = True

        if self.frame_start is None:
            self.frame_start = frame_data.number

        self.frame = frame_data.number

        self.process_left_turn(animal, roi, result)
        self.process_right_turn(animal, roi, result)

        if self.is_need_to_reset_center(animal, roi):
            self.context.transition_to(LostCenterState(self))

        if self.is_need_to_reset_mouse(animal, roi, result):
            result.trails.append([self.frame_start, self.frame])
            self.context.transition_to(AwaitingEnteringState())

        if result.total() == 10:
            self.context.transition_to(DoneState())

        result.frames_before_turn += 1

    def process_left_turn(self, animal: Animal, roi: Roi, result: Result) -> None:
        if self.is_mouse_turned_left(animal, roi, result):
            result.turns.append([self.frame_start, self.frame, 'L', result.frames_before_turn])
            result.trails.append([self.frame_start, self.frame])
            result.frames_before_turn = 0
            result.left_turn_count += 1

            self.transition_to_next_state(result, roi)

    def process_right_turn(self, animal: Animal, roi: Roi, result: Result) -> None:
        if self.is_mouse_turned_right(animal, roi, result):
            result.turns.append([self.frame_start, self.frame, 'R', result.frames_before_turn])
            result.trails.append([self.frame_start, self.frame])

            result.frames_before_turn = 0
            result.right_turn_count += 1

            self.transition_to_next_state(result, roi)

    def transition_to_next_state(self, result: Result, roi: Roi) -> None:
        self.context.transition_to(AwaitingCenterChange(roi.center))

    def is_mouse_turned_left(self, animal: Animal, roi: Roi, result: Result) -> bool:
        condition = roi.get_angle(animal) < self.left_turn_threshold and roi.can_score_turn(animal, result.scale)
        return self.left_turn_debouncer.check(condition)

    def is_mouse_turned_right(self, animal: Animal, roi: Roi, result: Result) -> bool:
        condition = roi.get_angle(animal) > self.right_turn_threshold and roi.can_score_turn(animal, result.scale)
        return self.right_turn_debouncer.check(condition)

    def is_need_to_reset_center(self, animal: Animal, roi: Roi) -> bool:
        condition = not roi.is_set
        return self.reset_center_debouncer.check(condition)

    def is_need_to_reset_mouse(self, animal: Animal, roi: Roi, result: Result) -> bool:
        condition = (roi.is_inside(animal) and roi.get_distance_to_neck(
            animal) > self.distance_to_neck * result.scale) or \
                    not animal.valid
        return self.reset_mouse_debouncer.check(condition)


class LostCenterState(State):

    def __init__(self, next_state: State):
        super().__init__()
        self.next_state = next_state
        self.center = None
        self.center_debouncer = Debouncer(threshold=10)
        self.roi_debouncer = Debouncer(threshold=10)

    def process(self, frame_data: FrameData, result: Result) -> None:
        result.state_name = 'Center is lost'
        roi = Roi(frame_data.data)

        if self.roi_is_set(roi):
            self.context.transition_to(self.next_state)

        if self.is_center_set(roi):
            self.context.transition_to(WaitingCenterState())

    def roi_is_set(self, roi: Roi) -> bool:
        return self.roi_debouncer.check(roi.is_set)

    def is_center_set(self, roi: Roi) -> bool:
        conditions = not isinstance(self.next_state, CountingTurnsState) and not roi.is_set
        return self.center_debouncer.check(conditions)


class DetectScaleState(State):
    def __init__(self, next_state: State):
        super().__init__()
        self.next_state = next_state
        self.state_debouncer = Debouncer(threshold=15)

    def process(self, frame_data: FrameData, result: Result) -> None:
        result.state_name = 'Detecting Scale'

        animal = Animal(frame_data.data)
        roi = Roi(frame_data.data)

        self.process_mouse(animal, roi, result)

    def process_mouse(self, animal: Animal, roi: Roi, result: Result) -> None:
        if self.is_mouse_enter_the_circle(animal, roi, result):
            result.is_set_scale = True
            result.scale = animal.get_scale()
            self.context.transition_to(AwaitingEnteringState())

    def is_mouse_enter_the_circle(self, animal: Animal, roi: Roi, result: Result) -> bool:
        condition = roi.can_start_scoring(animal, result.scale)
        return self.state_debouncer.check(condition)


class DoneState(State):
    def __init__(self):
        super().__init__()
        self.state_debouncer = Debouncer(threshold=60)

    def process(self, frame_data: FrameData, result: Result) -> None:
        result.state_name = 'Done'
        if self.is_done():
            frame_data.is_last = True

    def is_done(self) -> bool:
        return self.state_debouncer.check(True)


class WaitingCenterState(State):
    distance_threshold = 15

    def __init__(self):
        super().__init__()
        self.last_center = None
        self.state_debouncer = Debouncer(threshold=10)

    def process(self, frame_data: FrameData, result: Result) -> None:
        result.state_name = 'Waiting Center'
        roi = Roi(frame_data.data)
        self.process_center(roi)

    def process_center(self, roi: Roi) -> None:
        if not self.last_center and roi.is_set:
            self.last_center = roi.center

        if self.is_center_set(roi):
            self.context.transition_to(AwaitingMouseState())

        if self.state_debouncer.count == 0:
            self.last_center = None

    def is_center_set(self, roi: Roi) -> bool:
        condition = self.last_center is not None \
                    and is_point_in_boundaries(roi.center, self.last_center, self.distance_threshold) \
                    and roi.is_set
        return self.state_debouncer.check(condition)


class AwaitingEnteringState(State):

    def __init__(self):
        super().__init__()
        self.mouse_debouncer = Debouncer()
        self.center_debouncer = Debouncer(threshold=10)

    def process(self, frame_data: FrameData, result: Result) -> None:
        result.state_name = 'Awaiting Entering'
        result.is_counting = False
        animal = Animal(frame_data.data)
        roi = Roi(frame_data.data)
        self.process_mouse(animal, roi, result)

    def process_mouse(self, animal: Animal, roi: Roi, result: Result) -> None:
        if self.is_mouse_enter_the_circle(animal, roi, result):
            self.context.transition_to(CountingTurnsState())

        if self.is_center_set(roi):
            self.context.transition_to(WaitingCenterState())

    def is_mouse_enter_the_circle(self, animal: Animal, roi: Roi, result: Result) -> bool:
        condition = roi.can_score_turn(animal, result.scale)
        return self.mouse_debouncer.check(condition)

    def is_center_set(self, roi: Roi) -> bool:
        condition = not roi.is_set
        return self.center_debouncer.check(condition)


class AwaitingMouseState(State):

    def __init__(self):
        super().__init__()
        self.mouse_debouncer = Debouncer()

    def process(self, frame_data: FrameData, result: Result) -> None:
        result.state_name = 'Awaiting Animal'
        animal = Animal(frame_data.data)
        roi = Roi(frame_data.data)
        self.process_mouse(animal, roi, result)

    def process_mouse(self, animal: Animal, roi: Roi, result: Result) -> None:
        if self.is_mouse_set(animal, roi):
            if result.is_set_scale:
                self.context.transition_to(AwaitingEnteringState())
            else:
                self.context.transition_to(DetectScaleState(AwaitingEnteringState()))

    def is_mouse_set(self, animal: Animal, roi: Roi) -> bool:
        condition = roi.is_inside(animal)
        return self.mouse_debouncer.check(condition)


class AwaitingCenterChange(State):
    distance_to_neck = 250  # globals()['global_distance_to_neck']  # for mice 100 for rats 250
    distance_threshold = 60

    def __init__(self, center):
        super().__init__()
        self.center = center
        self.state_debouncer = Debouncer(threshold=20)

    def process(self, frame_data: FrameData, result: Result) -> None:
        result.state_name = 'Awaiting Center Change'
        animal = Animal(frame_data.data)
        roi = Roi(frame_data.data)
        if not self.center and roi.is_set:
            self.center = roi.center

        self.process_center(animal, roi, result)

    def process_center(self, animal: Animal, roi: Roi, result: Result) -> None:
        if self.is_center_changed(animal, roi, result):
            self.center = None
            self.context.transition_to(WaitingCenterState())

    def is_center_changed(self, animal: Animal, roi: Roi, result: Result) -> bool:
        condition = (not roi.is_inside(animal) and roi.get_distance(self.center) > 25) or \
                    (roi.is_inside(animal) and roi.get_distance_to_neck(
                        animal) > self.distance_to_neck * result.scale and -90 < roi.get_angle(
                        animal) < 90 and roi.get_distance(self.center) > 25) or not roi.is_set
        return self.state_debouncer.check(condition)
