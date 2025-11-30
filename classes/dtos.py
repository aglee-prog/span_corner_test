class BaseResult:

    def __init__(self):
        self.trails = None
        self.state_name = ''
        self.right_turn_count = 0
        self.left_turn_count = 0
        self.frames_count = 0
        self.start_frame = 0
        self.detected_frames = 0
        self.corrupted_frames_count = 0
        self.right_tendency_frames = 0
        self.left_tendency_frames = 0
        self.scale = 1
        self.corrupted = False
        self.trails = []
        self.circles = []

    def total(self):
        return self.right_turn_count + self.left_turn_count

    def detection_percent(self):
        if self.detected_frames > 0:
            return int(self.detected_frames / self.frames_count * 100)
        else:
            return 0

    def tendency_frames(self):
        return self.left_tendency_frames + self.right_tendency_frames

    def left_tendency_percent(self) -> int:
        frames = self.tendency_frames()
        if frames > 0:
            return int(self.left_tendency_frames / frames * 100)
        else:
            return 0

    def right_tendency_percent(self) -> int:
        frames = self.tendency_frames()
        if frames > 0:
            return int(self.right_tendency_frames / frames * 100)
        else:
            return 0

    def status(self) -> str:
        status = 'OK'

        if self.detection_percent() < 60:
            status = "Warning: Less than 60% of the frames with animal was detected"

        if not self.total() == 10:
            status = "Error: Total turns less than 10"

        if not self.detection_percent() < 20:
            status = "!!ERROR!! The animal is not recognized"

        return status


class FrameData:
    def __init__(self, number, length):
        self.number = number
        self.length = length

    fps = 0
    frame = 0
    number = 0
    start_frame = 0
    data = []
    is_last = False
    state_name = ''
