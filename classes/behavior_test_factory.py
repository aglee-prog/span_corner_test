from typing import Callable
from classes.behavior_test import BehaviorTest


class BehaviorTestFactory:
    registry = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        def inner_wrapper(wrapped_class: BehaviorTest) -> BehaviorTest:
            if name not in cls.registry:
                cls.registry[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def create(cls, name: str, **kwargs) -> BehaviorTest:
        if name not in cls.registry:
            raise RuntimeError(name + " test not found")

        exec_class = cls.registry[name]
        executor = exec_class(**kwargs)
        return executor
