"""Command line interface for europa1400_tools."""

from pathlib import Path
from typing import Annotated, Optional

import typer

from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.const import BIN_FILES
from europa1400_tools.extractor.file_extractor import FileExtractor

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

    common_options: CommonOptions = ctx.obj
    output_paths: list[Path] = []

    if not file_paths:
        file_paths = [
            common_options.game_resources_path / bin_file for bin_file in BIN_FILES
        ]

    for file_path in file_paths:
        output_subdir = common_options.extracted_path / file_path.stem
        extractor = FileExtractor()
        extracted_paths = extractor.extract(file_path, output_subdir)
        output_paths.extend(extracted_paths)

    return output_paths
