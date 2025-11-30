from __future__ import annotations
from abc import ABC, abstractmethod
from classes.dtos import FrameData, BaseResult


class StateContext:
    _state = None

    def __init__(self, state: State) -> None:
        self.transition_to(state)

    def transition_to(self, state: State):
        self._state = state
        self._state.context = self

    def process(self, data: FrameData, result: BaseResult):
        self._state.process(data, result)


class State(ABC):
    def __init__(self):
        self._context = None

    @property
    def context(self) -> StateContext:
        return self._context

    @context.setter
    def context(self, context: StateContext) -> None:
        self._context = context

    @abstractmethod
    def process(self, data: FrameData, result) -> None:
        pass
