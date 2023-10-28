from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Optional

import typer

from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.const import TargetFormat


@dataclass
class ConvertOptions(CommonOptions):
    _target_format: Annotated[
        Optional[str],
        typer.Option("--target-format", "-t", help="Target format."),
    ] = None
    _file_paths: Annotated[
        Optional[list[str]], typer.Argument(help="File paths to convert.")
    ] = None

    @property
    def target_format(self) -> TargetFormat | None:
        """Return the target format."""
        return TargetFormat.from_typer(self._target_format)

    @target_format.setter
    def target_format(self, value: TargetFormat) -> None:
        """Set the target format."""
        self._target_format = value.value[0]

    @property
    def file_paths(self) -> list[Path] | None:
        """Return the file paths to convert."""
        if self._file_paths is None or len(self._file_paths) == 0:
            return None
        return [Path(file_path) for file_path in self._file_paths]
