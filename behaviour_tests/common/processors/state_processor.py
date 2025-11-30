from classes.dtos import FrameData, BaseResult
from classes.state_context import StateContext, State


class StateProcessor:
    def __init__(self, state: State, result: BaseResult):
        self._result = result
        self._context = StateContext(state)

    def process(self, data: FrameData, **kwargs):
        self._context.process(data, self._result)
