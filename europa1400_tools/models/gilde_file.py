import shutil
from abc import ABC, abstractmethod
from dataclasses import _MISSING_TYPE, dataclass
from functools import cached_property
from pathlib import Path
from typing import Self

from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.cli.convert_options import ConvertOptions
from europa1400_tools.const import (
    CONVERTED_DIR,
    DECODED_DIR,
    EXTRACTED_DIR,
    PICKLE_EXTENSION,
)
from europa1400_tools.models.gilde_path import GildePath
from europa1400_tools.models.source_format import SourceFormat
from europa1400_tools.rich.progress import Progress


@dataclass
class GildeFile(ABC):
    path: GildePath
    source_format: SourceFormat

    @abstractmethod
    def extract(self, progress: Progress | None = None) -> list["GildeAsset"]:
        pass

    @classmethod
    def from_paths(cls, paths: list[GildePath]) -> list[Self]:
        files = []

        for path in paths:
            files.append(GildeFile.from_path(path))

        return files

    @classmethod
    def from_path(cls, path: GildePath) -> Self:
        if path.suffix == "":
            return GildeDirectory.from_path(path)
        elif path.is_archive:
            return GildeArchive.from_path(path)
        else:
            return GildeAsset.from_path(path)

    def __hash__(self) -> int:
        return hash(self.path)

    @staticmethod
    def from_typer(value: str | Path | GildePath | _MISSING_TYPE) -> Self | None:
        if isinstance(value, _MISSING_TYPE):
            return None

        if isinstance(value, (str, Path)):
            value = GildePath(value)

        return GildeFile.from_path(value)


@dataclass
class GildeDirectory(GildeFile):
    def extract(self, progress: Progress | None = None) -> list["GildeAsset"]:
        extracted_assets: list[GildeAsset] = []

        for contained_path in self.path.contained:
            asset = GildeAsset.from_path(contained_path)

            asset.extract(progress=progress)
            extracted_assets.append(asset)

        return extracted_assets

    @classmethod
    def from_path(cls, path: GildePath) -> Self:
        source_format = SourceFormat.from_path(path)

        if source_format is None:
            raise NotImplementedError(f"Could not determine source format for {path}")

        if path.exists():
            return GildeDirectory(path, source_format)

        source_path = GildeAsset._find_source_path(path, source_format)

        if source_path is None:
            raise FileNotFoundError(f"Could not find asset {path}")

        path = source_path.find(path)
        asset = GildeDirectory(path, source_format)
        return asset


@dataclass
class GildeArchive(GildeFile):
    @property
    def extracted_path(self) -> GildePath | None:
        return (
            CommonOptions.instance.output_path
            / EXTRACTED_DIR
            / self.source_format.output_path
        )

    def extract(self, progress: Progress | None = None) -> list["GildeAsset"]:
        extracted_paths: list[GildePath] = []
        extracted_assets: list[GildeAsset] = []

        for contained_path in self.path.contained:
            if progress is not None:
                progress.file_path = contained_path

            if (
                self.extracted_path / contained_path
            ).exists() and CommonOptions.instance.use_cache:
                if progress is not None:
                    progress.cached_file_count += 1
                extracted_paths.append(contained_path)
                continue

            self.path.extract(contained_path, self.extracted_path)
            extracted_paths.append(contained_path)

            if progress is not None:
                progress.completed_file_count += 1

        for extracted_path in extracted_paths:
            source_format = SourceFormat.from_path(extracted_path, self.path)
            asset = GildeAsset(extracted_path, source_format, source_path=self.path)
            extracted_assets.append(asset)

        return extracted_assets

    def extract_asset(self, asset: "GildeAsset"):
        self.path.extract(asset.path, self.extracted_path)

    @classmethod
    def from_path(cls, path: GildePath) -> Self:
        source_format = SourceFormat.from_path(path)

        if source_format is None:
            raise NotImplementedError(f"Could not determine source format for {path}")

        if path.exists():
            return GildeArchive(path, source_format)

        source_path = GildeAsset._find_source_path(path, source_format)

        if source_path is None:
            raise FileNotFoundError(f"Could not find asset {path}")

        path = source_path.find(path)
        asset = GildeArchive(path, source_format)
        return asset

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass
class GildeAsset(GildeFile):
    _source_path: GildePath | None = None

    def __init__(
        self,
        path: GildePath,
        source_format: SourceFormat,
        source_path: GildePath | None = None,
    ):
        super().__init__(path, source_format)
        self._source_path = source_path

    @cached_property
    def source_path(self) -> GildePath | None:
        if self._source_path is not None:
            return self._source_path

        return next(
            (
                source_path
                for source_path in self.source_format.source_paths
                if source_path.contains(self.path)
            ),
            None,
        )

    @property
    def source_archive(self) -> GildeArchive | None:
        if self.source_path is None:
            return None

        if self.source_path.is_archive:
            return GildeArchive(self.source_path, self.source_format)

        return None

    @property
    def extracted_base_path(self) -> GildePath | None:
        return (
            CommonOptions.instance.output_path
            / EXTRACTED_DIR
            / self.source_format.output_path
        )

    @property
    def extracted_path(self) -> GildePath | None:
        return self.extracted_base_path / self.path

    @property
    def decoded_base_path(self) -> GildePath | None:
        return (
            CommonOptions.instance.output_path
            / DECODED_DIR
            / self.source_format.output_path
        )

    @property
    def decoded_path(self) -> GildePath | None:
        return self.decoded_base_path / self.path.with_suffix(PICKLE_EXTENSION)

    @property
    def converted_base_path(self) -> GildePath | None:
        if ConvertOptions.instance is None:
            return None

        converted_base_path = CommonOptions.instance.output_path / CONVERTED_DIR

        if len(self.source_format.target_formats) > 1:
            converted_base_path /= ConvertOptions.instance.target_format.output_path

        return converted_base_path

    @property
    def converted_path(self) -> GildePath | None:
        if self.converted_base_path is None:
            return None

        return self.converted_base_path / self.path.parent / self.path.name

    def extract(self, progress: Progress | None = None):
        # if not self.source_archive:
        #     raise NotImplementedError("Asset is not contained in an archive.")

        if progress is not None:
            progress.file_path = self.path

        if self.extracted_path.exists() and CommonOptions.instance.use_cache:
            if progress is not None:
                progress.cached_file_count += 1
            return [self]

        self.extracted_path.parent.mkdir(parents=True, exist_ok=True)

        if self.source_archive is not None:
            self.source_archive.extract_asset(self)
        elif self.path.exists():
            shutil.copy(self.path, self.extracted_path)
        elif (self.source_path / self.path).exists():
            shutil.copy(self.source_path / self.path, self.extracted_path)
        else:
            raise FileNotFoundError(f"Could not find asset {self.path}")

        if progress is not None:
            progress.completed_file_count += 1

    def __hash__(self) -> int:
        return super().__hash__()

    @staticmethod
    def exists(path: GildePath) -> bool:
        source_format = SourceFormat.from_path(path)

        if source_format is None:
            return False

        if path.exists():
            return True

        if any(
            source_path.contains(path) for source_path in source_format.source_paths
        ):
            return True

        return False

    @staticmethod
    def from_paths(paths: list[GildePath | Path | str]) -> list[Self]:
        assets = []

        for path in paths:
            assets.append(GildeAsset.from_path(path))

        return assets

    @staticmethod
    def from_path(path: GildePath) -> Self:
        source_format = SourceFormat.from_path(path)

        if source_format is None:
            raise NotImplementedError(f"Could not determine source format for {path}")

        if path.exists():
            return GildeAsset(path, source_format)

        source_path = GildeAsset._find_source_path(path, source_format)

        if source_path is None:
            raise FileNotFoundError(f"Could not find asset {path}")

        path = source_path.find(path)

        asset = GildeAsset(path, source_format)
        return asset

    @staticmethod
    def _find_source_path(
        path: GildePath, source_format: SourceFormat
    ) -> GildePath | None:
        for source_path in source_format.source_paths:
            if source_path.contains(path):
                return source_path

        return None
