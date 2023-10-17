"""Base class for converters."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from timeit import default_timer as timer
from typing import TypeVar, final

from europa_1400_tools.common_options import CommonOptions
from europa_1400_tools.const import SourceFormat, TargetFormat

InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")
ConverterType = TypeVar("ConverterType", bound="BaseConverter")


class BaseConverter(ABC):
    """Base class for converters."""

    common_options: CommonOptions

    def __init__(self, common_options: CommonOptions):
        """Initialize the converter."""

        self.common_options = common_options

    @abstractmethod
    def convert_file(
        self,
        file_path: Path,
        output_path: Path,
        base_path: Path,
        target_format: TargetFormat,
        create_subdirectories: bool = False,
    ) -> list[Path]:
        """Convert file and export to output_path."""

    @final
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

            time_start = timer()

            converted_file_paths = self.convert_file(
                file_path,
                output_path,
                base_path,
                target_format,
                create_subdirectories,
            )

            time_end = timer()

            logging.debug(
                f"Converted {file_path} from {source_format} to {target_format}"
                + f" in {time_end - time_start:.2f} seconds."
            )

            if converted_file_paths is not None:
                output_paths.extend(converted_file_paths)

        return output_paths
