import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, Type, TypeVar

from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.const import PICKLE_EXTENSION
from europa1400_tools.construct.base_construct import BaseConstruct
from europa1400_tools.extractor.file_extractor import FileExtractor
from europa1400_tools.helpers import get_files, normalize
from europa1400_tools.rich.common import console
from europa1400_tools.rich.progress import Progress

ConstructType = TypeVar("ConstructType", bound=BaseConstruct)


class BaseDecoder(ABC, Generic[ConstructType]):
    """Base class for decoders."""

    construct_type: Type[ConstructType]

    def __init__(self, construct_type: Type[ConstructType]):
        self.construct_type = construct_type

    def decode_files(self, input_file_paths: list[Path] | None = None) -> list[Path]:
        """Decode files."""

        decoded_file_paths: list[Path] = []
        extracted_file_paths: list[Path] = []
        file_extractor = FileExtractor()

        if input_file_paths is None:
            if self.is_archive and self.extracted_path is not None:
                extracted_file_paths = file_extractor.extract(
                    self.game_path, self.extracted_path, self.file_suffix
                )
            elif self.is_single_file:
                extracted_file_paths = [self.game_path]
            else:
                extracted_file_paths = get_files(self.game_path, self.file_suffix)
        else:
            extractable_file_paths = [
                file_path.resolve().relative_to(self.extracted_path)
                if file_path.resolve().is_relative_to(self.extracted_path)
                else file_path
                for file_path in input_file_paths
                if normalize(file_path.suffix) == self.file_suffix
            ]
            extracted_game_file_paths = file_extractor.extract_files(
                extractable_file_paths,
                self.game_path,
                self.extracted_path,
                self.file_suffix,
            )
            extracted_file_paths.extend(extracted_game_file_paths)

        if len(extracted_file_paths) == 0:
            return []

        progress = Progress(
            title=f"Decoding {self.construct_type.__name__}",
            total_file_count=len(extracted_file_paths),
        )

        with progress:
            for extracted_file_path in extracted_file_paths:
                if normalize(extracted_file_path.suffix) != normalize(self.file_suffix):
                    continue

                if extracted_file_path.is_relative_to(self.extracted_path):
                    extracted_file_path = extracted_file_path.relative_to(
                        self.extracted_path
                    )

                progress.file_path = extracted_file_path

                decoded_output_path = (
                    self.decoded_path
                    if self.is_single_file
                    else (self.decoded_path / extracted_file_path).with_suffix(
                        PICKLE_EXTENSION
                    )
                )

                if decoded_output_path.exists() and CommonOptions.instance.use_cache:
                    decoded_file_paths.append(decoded_output_path)
                    progress.cached_file_count += 1
                    continue

                extracted_file_path = (
                    self.extracted_path / extracted_file_path
                    if not extracted_file_path.is_relative_to(self.extracted_path)
                    else extracted_file_path
                )
                decoded_value = self.decode_file(extracted_file_path)
                decoded_value.path = extracted_file_path.relative_to(
                    self.extracted_path
                )

                if not decoded_output_path.parent.exists():
                    decoded_output_path.parent.mkdir(parents=True)

                with open(decoded_output_path, "wb") as decoded_output_file:
                    pickle.dump(
                        decoded_value,
                        decoded_output_file,
                    )

                decoded_file_paths.append(decoded_output_path)

                progress.completed_file_count += 1

        return decoded_file_paths

    def decode_file(self, file_path: Path) -> ConstructType:
        """Decode file."""

        return self.construct_type.from_file(file_path)

    @property
    @abstractmethod
    def file_suffix(self) -> str:
        """File extension."""

    @property
    @abstractmethod
    def is_archive(self) -> bool:
        """Whether the assets are compressed into an archive."""

    @property
    @abstractmethod
    def is_single_file(self) -> bool:
        """Whether the assets are stored in a single file."""

    @property
    @abstractmethod
    def game_path(self) -> Path:
        """Path to the assets in the game directory."""

    @property
    @abstractmethod
    def extracted_path(self) -> Path | None:
        """Path to the extracted assets."""

    @property
    @abstractmethod
    def decoded_path(self) -> Path:
        """Path to the decoded assets."""
