from abc import abstractmethod, ABCMeta


class BehaviorTest(metaclass=ABCMeta):
    @abstractmethod
    def create(self, model: str, dir_path: str, csv_path: str) -> None:
        pass

    @abstractmethod
    def watch(self, model: str, video_path: str) -> None:
        pass
