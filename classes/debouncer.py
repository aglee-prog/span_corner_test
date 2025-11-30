class Debouncer:
    def __init__(self, threshold: int = 5):
        self.threshold = threshold
        self.counter = 0

    def check(self, condition: bool) -> bool:
        if condition:
            self.counter += 1
        else:
            self.counter = 0

        return self.counter > self.threshold

    def reset(self):
        self.counter = 0

    @property
    def count(self) -> int:
        return self.counter
