from dataclasses import dataclass, field
from typing import ClassVar, Generic, Self, Type, TypeVar, Union


class classproperty:
    def __init__(self, method):
        self.method = method

    def __get__(self, obj, cls=None):
        if cls is None:
            cls = type(obj)
        return self.method(cls)


@dataclass
class BaseOptions:
    instances: ClassVar[dict[Type[Self], Self]] = {}

    @classproperty
    def ATTRNAME(cls) -> str:
        return cls.__name__

    @classmethod
    @property
    def instance(cls) -> Self | None:
        if cls not in cls.instances:
            return None

        return cls.instances[cls]

    def __post_init__(self):
        self.instances[self.__class__] = self
