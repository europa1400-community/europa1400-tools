"""Base class for converters."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar

from europa_1400_tools.const import SourceFormat, TargetFormat
from europa_1400_tools.models import CommonOptions

InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")
ConverterType = TypeVar("ConverterType", bound="BaseConverter")


class BaseConverter(ABC):
    """Base class for converters."""

    common_options: CommonOptions

    def __init__(self, common_options: CommonOptions):
        """Initialize the converter."""

        self.common_options = common_options

    @staticmethod
    @abstractmethod
    def convert_file(
        file_path: Path,
        output_path: Path,
        base_path: Path,
        target_format: TargetFormat,
        create_subdirectories: bool = False,
    ) -> list[Path]:
        """Convert file and export to output_path."""

    def convert(
        self,
        file_paths: list[Path],
        output_path: Path,
        base_path: Path,
        source_format: SourceFormat,
        target_format: TargetFormat,
        create_subdirectories: bool = False,
    ) -> list[Path]:
        """Convert value and export to output_path."""

        output_paths: list[Path] = []

        for file_path in file_paths:
            logging.debug(
                f"Converting {file_path} from {source_format} to {target_format}..."
            )

            output_paths.extend(
                self.convert_file(
                    file_path,
                    output_path,
                    base_path,
                    target_format,
                    create_subdirectories,
                )
            )

        return output_paths
