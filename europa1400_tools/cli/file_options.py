from dataclasses import dataclass, field
from functools import cached_property
from typing import Annotated, Optional

import typer

from europa1400_tools.cli.base_options import BaseOptions
from europa1400_tools.models.gilde_file import GildeAsset, GildeFile
from europa1400_tools.models.gilde_path import GildePath


@dataclass
class FileOptions(BaseOptions):
    _files: Annotated[
        Optional[list[str]],
        typer.Argument(
            help="Assets to convert.",
        ),
    ] = None

    @cached_property
    def files(self) -> list[GildeFile] | None:
        """Return the Gilde files to convert."""

        if self._files is None or len(self._files) == 0:
            return None

        return [GildeFile.from_typer(value) for value in self._files]

    # _file_paths: Annotated[
    #     Optional[list[GildePath]],
    #     typer.Argument(help="File paths to convert.", parser=lambda x: GildePath(x)),
    # ] = None

    # _gilde_files: list[GildePath] | None = field(
    #     init=False,
    #     default=None,
    #     repr=False,
    #     hash=False,
    #     compare=False,
    #     metadata={"ignore": True},
    # )

    # @property
    # def file_paths(self) -> list[Path] | None:
    #     """Return the file paths to convert."""
    #     if self._file_paths is None or len(self._file_paths) == 0:
    #         return None
    #     return [GildePath(file_path) for file_path in self._file_paths]

    # @file_paths.setter
    # def file_paths(self, values: list[Path]) -> None:
    #     """Set the file paths to convert."""
    #     self._file_paths = [value.as_posix() for value in values]
    #     self._gilde_files = [GildePath(value) for value in values]

    # @property
    # def gilde_files(self) -> list[GildePath] | None:
    #     """Return the Gilde files to convert."""
    #     if self._file_paths is None or len(self._file_paths) == 0:
    #         return None

    #     if self._gilde_files is None or len(self._gilde_files) == 0:
    #         self._gilde_files = GildePath.from_paths(self.file_paths)

    #     return self._gilde_files

    # @property
    # def assets(self) -> list[GildeAsset] | None:
    #     """Return the Gilde assets to convert."""
    #     if self.gilde_files is None or len(self.gilde_files) == 0:
    #         return None

    #     return GildeAsset.load_many(self.gilde_files)
