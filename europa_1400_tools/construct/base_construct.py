from dataclasses import dataclass
from pathlib import Path
from typing import Type, TypeVar

from construct_typed import DataclassMixin, DataclassStruct

T = TypeVar("T", bound="BaseConstruct")


@dataclass
class BaseConstruct(DataclassMixin):
    """Base construct class."""

    @classmethod
    def from_file(cls: Type[T], file_path: Path) -> T:
        """Read the file and return the construct."""

        obj = DataclassStruct(cls).parse_file(file_path)
        return obj
