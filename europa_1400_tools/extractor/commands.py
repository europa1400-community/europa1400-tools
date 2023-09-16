"""Command line interface for europa_1400_tools."""

import logging
from pathlib import Path
from typing import Annotated, Optional

import typer

from europa_1400_tools.const import BIN_FILES
from europa_1400_tools.helpers import extract_zipfile
from europa_1400_tools.models import CommonOptions

app = typer.Typer()


@app.callback(invoke_without_command=True)
def extract(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]],
        typer.Option("--file", "-f", help=".bin files to extract."),
    ] = None,
) -> list[Path]:
    """Extract all files."""

    logging.info("Extracting all zipped files from the game.")

    common_options: CommonOptions = ctx.obj
    output_paths: list[Path] = []

    if not file_paths:
        file_paths = [
            common_options.resources_game_path / bin_file for bin_file in BIN_FILES
        ]

    for file_path in file_paths:
        output_subdir = common_options.extracted_path / file_path.stem
        extracted_paths = extract_file(file_path, output_subdir)
        output_paths.extend(extracted_paths)

    return output_paths


def extract_file(file_path: Path, output_path: Path) -> list[Path]:
    """Extract a single file."""

    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    if not output_path.exists():
        output_path.mkdir(parents=True)

    logging.info(f"Extracting {file_path.name} to {output_path}.")

    file_paths = extract_zipfile(file_path, output_path)

    return file_paths
