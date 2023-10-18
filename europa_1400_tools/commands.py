"""Common objects and functions for europa_1400_tools."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from europa_1400_tools.common_options import CommonOptions
from europa_1400_tools.const import DEFAULT_OUTPUT_PATH
from europa_1400_tools.converter.commands import app as convert_app
from europa_1400_tools.decoder.commands import app as decode_app
from europa_1400_tools.extractor.commands import app as extract_app
from europa_1400_tools.helpers import ask_for_game_path
from europa_1400_tools.preprocessor.commands import app as preprocess_app

app = typer.Typer()
app.add_typer(extract_app, name="extract")
app.add_typer(decode_app, name="decode")
app.add_typer(
    convert_app,
    name="convert",
)
app.add_typer(preprocess_app, name="preprocess")


@app.callback()
def main(
    ctx: typer.Context,
    game_path: Optional[Path] = typer.Option(
        None, "--game-path", "-g", help="Path to the game directory."
    ),
    output_path: Path = typer.Option(
        DEFAULT_OUTPUT_PATH, "--output-path", "-o", help="Path to the output directory."
    ),
    use_cache: bool = typer.Option(
        False, "--use-cache", "-c", help="Use cached files."
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output."),
) -> None:
    """Main entry point."""

    # validate arguments

    if "--help" in sys.argv:
        return

    if game_path is None:
        game_path = ask_for_game_path()

    ctx.obj = CommonOptions(
        game_path=game_path.resolve(),
        output_path=output_path.resolve(),
        use_cache=use_cache,
        verbose=verbose,
    )
