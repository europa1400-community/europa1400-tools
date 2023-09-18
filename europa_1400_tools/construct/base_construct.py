import json
from abc import ABC
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Type, TypeVar

import construct as cs
from construct_typed import DataclassMixin, DataclassStruct, csfield

T = TypeVar("T", bound="BaseConstruct")


@dataclass
class BaseConstruct(ABC, DataclassMixin):
    """Base construct class."""

    path: Path = csfield(cs.Computed(lambda ctx: Path(ctx._io.name)))

    @classmethod
    def from_file(cls: Type[T], file_path: Path) -> T:
        """Read the file and return the construct."""

        obj = DataclassStruct(cls).parse_file(
            file_path,
        )

        return obj

    @property
    def ignored_fields(self) -> list[str]:
        """Return the list of ignored fields."""

        return []

    def _dict_factory(self, data: list[tuple[str, Any]]) -> dict:
        """Return the dict representation of the construct."""

        obj_dict = dict(data)

        for field in self.ignored_fields:
            obj_dict.pop(field, None)

        return obj_dict

    def to_dict(self) -> dict:
        """Return the dict representation of the construct."""

        obj_dict = asdict(self, dict_factory=self._dict_factory)

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
