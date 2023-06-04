"""Commands for the decoder."""

import pickle
from pathlib import Path
from typing import Annotated, Optional

import typer

from europa_1400_tools.const import PICKLE_EXTENSION, SBF_EXTENSION, SFX_DIR
from europa_1400_tools.construct.sbf import Sbf
from europa_1400_tools.extractor.commands import extract
from europa_1400_tools.helpers import get_files, rebase_path
from europa_1400_tools.models import CommonOptions

app = typer.Typer()


@app.command("all")
def decode_all() -> None:
    """Decode all files."""

    raise NotImplementedError()


@app.command("sfx")
def decode_sfx(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]], typer.Option(help=".sbf files to decode.")
    ] = None,
) -> list[Path]:
    """Decode SFX files."""

    common_options: CommonOptions = ctx.obj
    decoded_sfx_path = common_options.decoded_path / SFX_DIR
    pickle_output_paths: list[Path] = []

    if not file_paths:
        file_paths = get_files(common_options.sfx_game_path, SBF_EXTENSION)

        for file in file_paths:
            typer.echo(f"Decoding {file}...")

            sbf = Sbf.from_file(file)
            pickle_output_path = rebase_path(
                file, common_options.sfx_game_path, decoded_sfx_path
            ).with_suffix(PICKLE_EXTENSION)
            pickle_output_paths.append(pickle_output_path)

            if not pickle_output_path.parent.exists():
                pickle_output_path.parent.mkdir(parents=True)

            with open(pickle_output_path, "wb") as pickle_output_file:
                pickle.dump(
                    sbf,
                    pickle_output_file,
                )

        return pickle_output_paths

    for file in file_paths:
        typer.echo(f"Decoding {file}...")

        sbf = Sbf.from_file(file)
        pickle_output_path = decoded_sfx_path / Path(file.name).with_suffix(
            PICKLE_EXTENSION
        )

        if not pickle_output_path.parent.exists():
            pickle_output_path.parent.mkdir(parents=True)

        with open(pickle_output_path, "wb") as pickle_output_file:
            pickle.dump(
                sbf,
                pickle_output_file,
            )

        pickle_output_paths.append(pickle_output_path)

    return pickle_output_paths
