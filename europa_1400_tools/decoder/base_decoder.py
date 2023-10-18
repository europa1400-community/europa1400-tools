import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, Type, TypeVar

from europa_1400_tools.common_options import CommonOptions
from europa_1400_tools.const import PICKLE_EXTENSION
from europa_1400_tools.construct.base_construct import BaseConstruct
from europa_1400_tools.extractor.file_extractor import FileExtractor
from europa_1400_tools.helpers import get_files, normalize
from europa_1400_tools.rich.progress import Progress

ConstructType = TypeVar("ConstructType", bound=BaseConstruct)


class BaseDecoder(ABC, Generic[ConstructType]):
    """Base class for decoders."""

    common_options: CommonOptions
    construct_type: Type[ConstructType]

    def __init__(
        self, common_options: CommonOptions, construct_type: Type[ConstructType]
    ):
        self.common_options = common_options
        self.construct_type = construct_type

    def decode_files(self, file_paths: list[Path] | None = None) -> list[Path]:
        """Decode files."""

        decoded_file_paths: list[Path] = []

        if file_paths is None:
            if self.is_archive and self.extracted_path is not None:
                file_extractor = FileExtractor(self.common_options)
                file_paths = file_extractor.extract(
                    self.game_path, self.extracted_path, self.file_suffix
                )
            elif self.is_single_file:
                file_paths = [self.game_path]
            else:
                file_paths = get_files(self.game_path, self.file_suffix)
        else:
            file_paths = [
                file_path
                for file_path in file_paths
                if normalize(file_path.suffix) == normalize(self.file_suffix)
            ]

        progress = Progress(
            title=f"Decoding {self.construct_type.__name__}",
            total_file_count=len(file_paths),
        )

        with progress:
            for file_path in file_paths:
                if normalize(file_path.suffix) != normalize(self.file_suffix):
                    continue

                base_path = (
                    self.extracted_path
                    if self.is_archive and self.extracted_path is not None
                    else self.game_path.parent
                    if self.is_single_file
                    else self.game_path
                )
                relative_file_path = file_path.relative_to(base_path)

                progress.file_path = relative_file_path

                decoded_output_path = (
                    self.decoded_path
                    if self.is_single_file
                    else (self.decoded_path / relative_file_path).with_suffix(
                        PICKLE_EXTENSION
                    )
                )

                if decoded_output_path.exists() and self.common_options.use_cache:
                    decoded_file_paths.append(decoded_output_path)
                    progress.cached_file_count += 1
                    continue

                decoded_value = self.decode_file(file_path)
                decoded_value.path = relative_file_path

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
