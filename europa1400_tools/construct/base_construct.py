import json
from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Type, TypeVar

import construct as cs
from construct_typed import DataclassMixin, DataclassStruct, csfield

from europa1400_tools.construct.common import asdict

T = TypeVar("T", bound="BaseConstruct")


@dataclass
class BaseConstruct(ABC, DataclassMixin):
    """Base construct class."""

    path: Path = csfield(cs.Computed(lambda ctx: Path(ctx._io.name)))

    @classmethod
    def from_file(cls: Type[T], file_path: Path) -> T:
        """Read the file and return the construct."""

        obj: T = DataclassStruct(cls).parse_file(
            file_path,
        )

        return obj

    def to_dict(self) -> dict:
        """Return the dict representation of the construct."""

        obj_dict = asdict(self)

        return obj_dict

    def to_json(self) -> str:
        """Return the json representation of the construct."""

        obj_dict = self.to_dict()
        obj_json = json.dumps(obj_dict, indent=4, default=self.encode_construct)

        return obj_json

    @staticmethod
    def encode_construct(value: Any):
        try:
            json.dumps(value)
            return value
        except TypeError:
            return None
