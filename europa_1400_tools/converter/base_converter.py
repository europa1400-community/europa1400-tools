"""Base class for converters."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")


class BaseConverter(ABC, Generic[InputType, OutputType]):
    """Base class for converters."""

    @staticmethod
    @abstractmethod
    def convert(value: InputType, **kwargs) -> OutputType:
        """Convert value to another format."""

    @staticmethod
    @abstractmethod
    def convert_and_export(value: InputType, output_path: Path, **kwargs) -> list[Path]:
        """Convert value and export to output_path."""
