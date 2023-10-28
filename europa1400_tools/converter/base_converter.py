"""Base class for converters."""

import logging
import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from timeit import default_timer as timer
from typing import Generic, Type, TypeVar, final

from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.cli.convert_options import ConvertOptions
from europa1400_tools.const import PICKLE_EXTENSION, SourceFormat, TargetFormat
from europa1400_tools.construct.base_construct import BaseConstruct
from europa1400_tools.decoder.base_decoder import BaseDecoder
from europa1400_tools.helpers import normalize
from europa1400_tools.rich.common import console
from europa1400_tools.rich.progress import Progress

InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")
ConverterType = TypeVar("ConverterType", bound="BaseConverter")
ConstructType = TypeVar("ConstructType", bound=BaseConstruct)
DecoderType = TypeVar("DecoderType", bound=BaseDecoder)


class BaseConverter(ABC, Generic[ConstructType]):
    """Base class for converters."""

    construct_type: Type[ConstructType]
    decoder_type: Type[DecoderType]

    def __init__(
        self,
        construct_type: Type[ConstructType],
        decoder_type: Type[DecoderType],
    ):
        """Initialize the converter."""

        self.construct_type = construct_type
        self.decoder_type = decoder_type

    def convert_files(self, file_paths: list[Path] | None = None) -> list[Path]:
        """Convert files."""

        output_file_paths: list[Path] = []

        decoder = self.decoder_type()

        file_paths = file_paths or ConvertOptions.instance.file_paths or []
        extracted_file_paths: list[Path] = []
        decoded_file_paths: list[Path] = []

        if not any(file_paths):
            decoded_file_paths = decoder.decode_files()
        else:
            for file_path in file_paths:
                if (
                    normalize(file_path.suffix)
                    not in [
                        normalize(decoder.file_suffix),
                        normalize(PICKLE_EXTENSION),
                    ]
                    or file_path.is_dir()
                ):
                    console.print(
                        f"Skipping {file_path}: not a {decoder.file_suffix} "
                        + f"or {PICKLE_EXTENSION} file"
                    )
                    continue

                if normalize(file_path.suffix) == normalize(decoder.file_suffix):
                    extracted_file_paths.append(file_path)
                    continue

                if normalize(file_path.suffix) == normalize(PICKLE_EXTENSION):
                    decoded_file_paths.append(file_path)
                    continue

        if any(extracted_file_paths):
            decoded_extracted_file_paths = decoder.decode_files(extracted_file_paths)
            decoded_file_paths.extend(decoded_extracted_file_paths)

        self.preprocess(decoded_file_paths)

        progress = Progress(
            title=f"Converting {self.construct_type.__name__}",
            total_file_count=len(decoded_file_paths),
        )

        with progress:
            for file_path in decoded_file_paths:
                if normalize(file_path.suffix) != normalize(PICKLE_EXTENSION):
                    raise ValueError(f"Unknown file extension: {file_path.suffix}")

                with file_path.open("rb") as file:
                    value: BaseConstruct = pickle.load(file)

                progress.file_path = value.path

                converted_output_path = self.converted_path / value.path.parent

                if self.is_single_output_file:
                    converted_output_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    converted_output_path.mkdir(parents=True, exist_ok=True)

                converted_file_paths = self.convert(value, converted_output_path)

                output_file_paths.extend(converted_file_paths)

                progress.completed_file_count += 1

        return output_file_paths

    @property
    def decoded_path(self) -> Path:
        """Return the decoded path."""

        return ConvertOptions.instance.decoded_path

    @property
    def converted_path(self) -> Path:
        """Return the converted path."""

        return ConvertOptions.instance.converted_path

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
