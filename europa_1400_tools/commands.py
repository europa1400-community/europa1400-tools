"""Common objects and functions for europa_1400_tools."""

import sys
from pathlib import Path
from typing import Optional

import typer

from europa_1400_tools.const import DEFAULT_OUTPUT_PATH
from europa_1400_tools.decoder.commands import app as decode_app
from europa_1400_tools.extractor.commands import app as extract_app
from europa_1400_tools.helpers import ask_for_game_path
from europa_1400_tools.models import CommonOptions

app = typer.Typer()
app.add_typer(extract_app, name="extract")
app.add_typer(decode_app, name="decode")


@app.callback()
def main(
    ctx: typer.Context,
    game_path: Optional[Path] = typer.Option(
        None, "--game-path", "-g", help="Path to the game directory."
    ),
    output_path: Path = typer.Option(
        DEFAULT_OUTPUT_PATH, "--output-path", "-o", help="Path to the output directory."
    ),
) -> None:
    """Main entry point."""

    # validate arguments

    if "--help" in sys.argv:
        return

    if game_path is None:
        game_path = ask_for_game_path()

    ctx.obj = CommonOptions(game_path=game_path, output_path=output_path)
