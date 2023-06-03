"""Command line interface for europa_1400_tools."""

from pathlib import Path
from typing import Annotated

import typer

from europa_1400_tools.const import BIN_FILES, EXTRACTED_DIR
from europa_1400_tools.helpers import extract_zipfile
from europa_1400_tools.models import CommonOptions

app = typer.Typer()


@app.callback(invoke_without_command=True)
def extract(
    ctx: typer.Context,
    files: Annotated[list[str], "files to extract"] = typer.Option(
        [], "--file", "-f", help="Files to extract."
    ),
) -> None:
    """Extract all files."""

    typer.echo("Extracting all zipped files from the game.")

    common_options: CommonOptions = ctx.obj

    if not files:
        files = BIN_FILES

    for file in files:
        bin_path = common_options.resources_game_path / file
        output_subdir = common_options.extracted_path / bin_path.stem

        if not bin_path.exists():
            typer.echo(f"File {bin_path} does not exist.")
            continue

        if not output_subdir.exists():
            output_subdir.mkdir(parents=True)

        typer.echo(f"Extracting {bin_path} to {output_subdir}.")

        extract_zipfile(bin_path, output_subdir)


def extract_file(file_path: Path, output_path: Path) -> None:
    """Extract a single file."""

    if not file_path.exists():
        typer.echo(f"File {file_path} does not exist.")
        return

    output_path = output_path / EXTRACTED_DIR / file_path.stem

    if not output_path.exists():
        output_path.mkdir(parents=True)

    typer.echo(f"Extracting {file_path} to {output_path}.")

    extract_zipfile(file_path, output_path)
