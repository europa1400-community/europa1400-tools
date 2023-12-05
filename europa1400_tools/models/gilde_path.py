import os
import pathlib
import re
from dataclasses import _MISSING_TYPE, dataclass
from functools import cached_property
from typing import Self
from zipfile import ZipFile, is_zipfile

ARCHIVE_SUFFIXES = [".bin", ".bin0", ".bin1"]


@dataclass
class GildePath(pathlib.Path):
    _flavour = pathlib._windows_flavour if os.name == "nt" else pathlib._posix_flavour

    def __new__(cls, *args):
        if len(args) == 1:
            if isinstance(args, tuple):
                args = list(args)
            if isinstance(args[0], pathlib.Path):
                args[0] = args[0].as_posix()

        return super(GildePath, cls).__new__(cls, *args)

    def __init__(self, *args):
        super().__init__()

    @property
    def contained(self, suffix: str | None = None) -> list[Self]:
        paths: list[Self] = []

        if self.is_dir():
            paths = self._dir_contained(suffix)

        if self.is_archive:
            paths = self._archive_contained(suffix)

        paths = list(
            map(
                lambda path: path.relative_to(self)
                if path.is_relative_to(self)
                else path,
                paths,
            )
        )

        return paths

    @cached_property
    def is_archive(self) -> bool:
        """Check if the file is an archive."""

        # return is_zipfile(self.as_posix()) or any(
        #     map(self.has_suffix, ARCHIVE_SUFFIXES)
        # )
        return any(map(self.has_suffix, ARCHIVE_SUFFIXES))

    def has_parent(self) -> bool:
        return (
            self.parent != self
            and self.parent != GildePath(".")
            and self.parent != GildePath("/")
        )

    def can_shift_left(self) -> bool:
        return len(self.parts) > 1

    def has_suffix(self, other: Self | str, index: int | None = None) -> bool:
        if isinstance(other, GildePath):
            other = other.suffix

        if index is not None and index >= len(self.suffixes):
            return False

        own = self.suffixes[index] if index is not None else self.suffix

        return GildePath.normalize(
            own, perform_remove_non_alphanumeric=True
        ) == GildePath.normalize(other, perform_remove_non_alphanumeric=True)

    def has_suffixes(self, others: list[Self | pathlib.Path | str]) -> bool:
        return all([self.has_suffix(suffix, i) for i, suffix in enumerate(others)])

    def has_stem(self, other: Self | str) -> bool:
        if isinstance(other, (GildePath, pathlib.Path)):
            other = other.stem

        return GildePath.normalize(self.stem) == GildePath.normalize(other)

    def has_name(self, other: Self | pathlib.Path | str) -> bool:
        if isinstance(other, (GildePath, pathlib.Path)):
            other = other.name

        return GildePath.normalize(self.name) == GildePath.normalize(other)

    def endswith(self, path: Self) -> bool:
        """Check if the path ends with another path."""

        return self.as_posix().endswith(path.as_posix())

    def rebase(self, old_base: Self, new_base: Self) -> Self:
        was_absolute = self.is_absolute()
        path = self.resolve()

        old_base = old_base.resolve()
        new_base = new_base.resolve()

        if not path.is_relative_to(old_base):
            raise ValueError(f"{path} is not relative to {old_base}")

        path = path.relative_to(old_base)
        path = new_base / path

        if was_absolute:
            path = path.resolve()

        return path

    def contains(self, path: Self) -> bool:
        """Check if the path contains another path."""

        if self.endswith(path):
            return True

        if self.is_dir():
            return self._dir_contains(path)

        if self.is_archive:
            return self._archive_contains(path)

        return False

    def find(self, path: Self, relative: bool = True) -> Self | None:
        """Find a path in a directory or archive."""

        if path.is_absolute():
            return None

        result: Self | None = None

        if self.endswith(path):
            return self

        if path.resolve().is_relative_to(self.resolve()):
            path = path.resolve().relative_to(self.resolve())

        if self.is_dir():
            result = self._dir_find(path)

            if result is not None and result.is_relative_to(self):
                result = result.relative_to(self)
        elif self.is_archive:
            result = self._archive_find(path)
        elif self.endswith(path):
            result = self

        if not relative:
            result = self / result

        return result

    def extract(self, path: Self, output_path: Self) -> Self:
        with ZipFile(self, "r") as zip_file:
            try:
                zip_file.extract(path.as_posix(), output_path)
            except KeyError:
                raise FileNotFoundError(f"Could not find {path} in {self}")
            return path

    def extract_all(self, output_path: Self) -> list[Self]:
        with ZipFile(self, "r") as zip_file:
            zip_file.extractall(output_path)

        return [path for path in output_path.contained]

    def shift_left(self) -> Self:
        return self.relative_to(GildePath(self.parts[0]))

    def _dir_contained(self, suffix: str | None = None) -> list[Self]:
        paths: list[Self] = []

        for path in self.iterdir():
            if path.is_dir():
                paths.extend(path._dir_contained(suffix))
                continue
            if suffix is None or path.has_suffix(suffix):
                paths.append(path)

        return paths

    def _dir_contains(self, path: Self) -> bool:
        return self._dir_find(path) is not None

    def _dir_find(self, path: Self) -> Self | None:
        if (self / path).exists():
            return self / path

        subdirectories = [x for x in self.iterdir() if x.is_dir()]

        for subdirectory in subdirectories:
            if subdirectory.contains(path):
                return subdirectory._dir_find(path)

        return None

    def _archive_contained(self, suffix: str | None = None) -> list[Self]:
        paths: list[Self] = []

        with ZipFile(self, "r") as zip_file:
            for file_name in zip_file.filelist:
                path = GildePath(file_name.filename)
                if file_name.is_dir():
                    continue
                if suffix is None or path.has_suffix(suffix):
                    paths.append(path)

        return paths

    def _archive_contains(self, path: Self) -> bool:
        return self._archive_find(path) is not None

    def _archive_find(self, path: Self) -> Self | None:
        with ZipFile(self, "r") as zip_file:
            zip_paths = list(map(GildePath, zip_file.namelist()))

        found_path = next(
            (zip_path for zip_path in zip_paths if zip_path.endswith(path)), None
        )

        return found_path

    def __eq__(self, __value: object) -> bool:
        if __value is None:
            return False

        if isinstance(__value, str):
            return GildePath.normalize(self.as_posix()) == GildePath.normalize(__value)

        if isinstance(__value, GildePath):
            return GildePath.normalize(self.as_posix()) == GildePath.normalize(
                __value.as_posix()
            ) or GildePath.normalize(self.resolve().as_posix()) == GildePath.normalize(
                __value.resolve().as_posix()
            )

        raise NotImplementedError

    def __repr__(self) -> str:
        return (
            super()
            .__repr__()
            .replace("PosixPath", "GildePath")
            .replace("WindowsPath", "GildePath")
        )

    def __hash__(self) -> int:
        return super().__hash__()

    @staticmethod
    def from_typer(value: str | _MISSING_TYPE) -> Self | None:
        if isinstance(value, _MISSING_TYPE):
            return None
        path = GildePath(value)
        return path

    @staticmethod
    def normalize(
        path: Self | pathlib.Path | str,
        perform_strip_non_ascii: bool = True,
        perform_lower: bool = True,
        perform_remove_suffix: bool = False,
        perform_remove_non_alphanumeric: bool = False,
    ) -> str:
        """Normalizes the specified string."""

        if isinstance(path, (GildePath, pathlib.Path)):
            path = path.as_posix()

        if perform_strip_non_ascii:
            path = GildePath.strip_non_ascii(path)

        if perform_lower:
            path = path.lower()

        if perform_remove_suffix:
            path = GildePath(path).stem

        if perform_remove_non_alphanumeric:
            path = re.sub(r"[^a-zA-Z0-9]", "", path)

        return path

    @staticmethod
    def strip_non_ascii(input_string):
        stripped_string = re.sub(r"[^\x00-\x7F]+", "", input_string)
        return stripped_string
