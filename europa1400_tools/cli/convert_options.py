from dataclasses import dataclass
from typing import Annotated, Optional

import typer

from europa1400_tools.cli.base_options import BaseOptions
from europa1400_tools.models.target_format import TargetFormat, TargetFormats


@dataclass
class ConvertOptions(BaseOptions):
    _target_format: Annotated[
        Optional[str],
        typer.Option("--target-format", "-t", help="Target format."),
    ] = None

    @property
    def target_format(self) -> TargetFormat | None:
        """Return the target format."""

        if self._target_format is None:
            return None

        target_format = TargetFormats.from_typer(self._target_format)

        return target_format

    @target_format.setter
    def target_format(self, value: TargetFormat) -> None:
        """Set the target format."""
        self._target_format = value.command
