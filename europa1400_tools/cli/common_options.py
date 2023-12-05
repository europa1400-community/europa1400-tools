from dataclasses import dataclass, field
from tkinter import Tk, filedialog
from typing import Annotated, ClassVar, Optional, Self

import typer

from europa1400_tools.cli.base_options import BaseOptions
from europa1400_tools.const import DEFAULT_OUTPUT_PATH
from europa1400_tools.models.gilde_path import GildePath


@dataclass
class CommonOptions(BaseOptions):
    """Dataclass defining CLI options used by all commands."""

    _game_path: Annotated[
        str,
        typer.Option(
            "--game-path",
            "-g",
            help="Path to the game directory.",
        ),
    ] = None
    _output_path: Annotated[
        str,
        typer.Option(
            "--output-path",
            "-o",
            help="Path to the output directory.",
        ),
    ] = DEFAULT_OUTPUT_PATH
    use_cache: Annotated[
        Optional[bool], typer.Option("--use-cache", "-c", help="Use cached files.")
    ] = False
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Verbose output.")
    ] = False

    @property
    def game_path(self) -> GildePath:
        """Return the path to the game directory."""

        if self._game_path is None:
            self._game_path = self.ask_for_game_path()

        if self._game_path is None:
            raise ValueError("Game path is None")

        return self._game_path

    @game_path.setter
    def game_path(self, value: GildePath | str) -> None:
        """Set the path to the game directory."""
        if isinstance(value, str):
            value = GildePath(value)
        self._game_path = value

    @property
    def output_path(self) -> GildePath:
        """Return the path to the output directory."""
        return GildePath(self._output_path)

    @output_path.setter
    def output_path(self, value: GildePath | str) -> None:
        """Set the path to the output directory."""
        if isinstance(value, GildePath):
            value = value.as_posix()
        self._output_path = value

    @classmethod
    def from_context(cls, ctx: typer.Context) -> "CommonOptions":
        if (common_params_dict := getattr(ctx, "common_params", None)) is None:
            raise ValueError("Context missing common_params")

        return cls(**common_params_dict)

    @staticmethod
    def ask_for_game_path() -> GildePath:
        """Ask the user for the game path using a file dialog."""

        root = Tk()
        root.withdraw()

        game_path = filedialog.askdirectory(title="Select the game directory")

        if not game_path:
            raise RuntimeError("No game path selected")

        return GildePath(game_path)
