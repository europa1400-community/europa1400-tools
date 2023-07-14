from dataclasses import dataclass
from pathlib import Path
from typing import IO, Type, TypeVar

import construct as cs
from construct_typed import DataclassMixin, DataclassStruct, csfield

T = TypeVar("T", bound="BaseConstruct")


@dataclass
class BaseConstruct(DataclassMixin):
    """Base construct class."""

    path: Path = csfield(cs.Computed(lambda ctx: Path(ctx._io.name)))

    @classmethod
    def from_file(cls: Type[T], file_path: Path) -> T:
        """Read the file and return the construct."""

        obj = DataclassStruct(cls).parse_file(
            file_path,
        )

        return obj
