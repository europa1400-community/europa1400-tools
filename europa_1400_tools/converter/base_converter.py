"""Base class for converters."""

import logging
import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from timeit import default_timer as timer
from typing import Generic, Type, TypeVar, final

from europa_1400_tools.common_options import CommonOptions
from europa_1400_tools.const import PICKLE_EXTENSION, SourceFormat, TargetFormat
from europa_1400_tools.construct.base_construct import BaseConstruct
from europa_1400_tools.decoder.base_decoder import BaseDecoder
from europa_1400_tools.helpers import normalize
from europa_1400_tools.rich.progress import Progress

InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")
ConverterType = TypeVar("ConverterType", bound="BaseConverter")
ConstructType = TypeVar("ConstructType", bound=BaseConstruct)
DecoderType = TypeVar("DecoderType", bound=BaseDecoder)


class BaseConverter(ABC, Generic[ConstructType]):
    """Base class for converters."""

    common_options: CommonOptions
    construct_type: Type[ConstructType]

    def __init__(
        self,
        common_options: CommonOptions,
        construct_type: Type[ConstructType],
        decoder_type: Type[DecoderType],
    ):
        """Initialize the converter."""

        self.common_options = common_options
        self.construct_type = construct_type
        self.decoder_type = decoder_type

    def convert_files(self, file_paths: list[Path] | None) -> list[Path]:
        """Convert files."""

        output_file_paths: list[Path] = []

        decoder = self.decoder_type(self.common_options)

        if file_paths is None or not any(file_paths):
            file_paths = decoder.decode_files()
        else:
            file_paths = [
                file_paths
                for file_path in file_paths
                if normalize(file_path.suffix) == normalize(PICKLE_EXTENSION)
            ]

        self.preprocess(file_paths)

        progress = Progress(
            title=f"Converting {self.construct_type.__name__}",
            total_file_count=len(file_paths),
        )

        with progress:
            for file_path in file_paths:
                if normalize(file_path.suffix) != normalize(PICKLE_EXTENSION):
                    continue

                base_path = self.decoded_path
                relative_path = file_path.relative_to(base_path)
                progress.file_path = relative_path

                converted_output_path = self.converted_path / relative_path.parent

                if self.is_single_output_file:
                    converted_output_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    converted_output_path.mkdir(parents=True, exist_ok=True)

                with file_path.open("rb") as file:
                    value = pickle.load(file)

                converted_file_paths = self.convert(value, converted_output_path)

                output_file_paths.extend(converted_file_paths)

                progress.completed_file_count += 1

        return output_file_paths

    @property
    def decoded_path(self) -> Path:
        """Return the decoded path."""

        return self.common_options.decoded_path

    @property
    def converted_path(self) -> Path:
        """Return the converted path."""

        return self.common_options.converted_path

    @property
    def is_single_output_file(self) -> bool:
        """Return whether the output is a single file."""

        return True

    def preprocess(
        self,
        file_paths: list[Path],
    ) -> None:
        """Preprocess files."""

    @abstractmethod
    def convert(
        self,
        value: ConstructType,
        output_path: Path,
        base_path: Path,
    ) -> list[Path]:
        """Convert file and export to output_path."""

    # @final
    # def convert(
    #     self,
    #     file_paths: list[Path],
    #     output_path: Path,
    #     base_path: Path,
    #     source_format: SourceFormat,
    #     target_format: TargetFormat,
    #     create_subdirectories: bool = False,
    # ) -> list[Path]:
    #     """Convert value and export to output_path."""

    #     output_paths: list[Path] = []

    #     for file_path in file_paths:
    #         logging.debug(
    #             f"Converting {file_path} from {source_format} to {target_format}..."
    #         )

    #         time_start = timer()

    #         converted_file_paths = self.convert_file(
    #             file_path,
    #             output_path,
    #             base_path,
    #             target_format,
    #             create_subdirectories,
    #         )

    #         time_end = timer()

    #         logging.debug(
    #             f"Converted {file_path} from {source_format} to {target_format}"
    #             + f" in {time_end - time_start:.2f} seconds."
    #         )

    #         if converted_file_paths is not None:
    #             output_paths.extend(converted_file_paths)

    #     return output_paths
