"""Commands for converting files"""

import pickle
from pathlib import Path
from typing import Annotated, Optional

import typer

from europa_1400_tools.const import (
    GFX_EXTENSION,
    OUTPUT_GFX_DIR,
    PICKLE_EXTENSION,
    SBF_EXTENSION,
    SFX_DIR,
    TargetAudioFormat,
)
from europa_1400_tools.construct.sbf import Sbf
from europa_1400_tools.converter.gfx_converter import GfxConverter
from europa_1400_tools.converter.sbf_converter import SbfConverter
from europa_1400_tools.decoder.commands import decode_gfx, decode_sfx
from europa_1400_tools.helpers import rebase_path
from europa_1400_tools.models import CommonOptions

app = typer.Typer()


@app.command("all")
def convert_all():
    """Convert all files"""

    raise NotImplementedError()


@app.command("gfx")
def convert_gfx(
    ctx: typer.Context,
    file_path: Annotated[
        Optional[Path],
        typer.Option("--file", "-f", help=".gfx or .pickle file to convert."),
    ] = None,
) -> list[Path]:
    """Convert GFX file to PNG files"""

    common_options: CommonOptions = ctx.obj
    output_file_paths: list[Path] = []

    if not file_path:
        file_path = common_options.gfx_game_path

    typer.echo(f"Converting {file_path}...")

    if file_path.suffix not in [GFX_EXTENSION, PICKLE_EXTENSION]:
        raise ValueError(f"Unknown file extension: {file_path.suffix}")
    elif file_path.suffix == GFX_EXTENSION:
        file_path = decode_gfx(ctx, file_path)[0]

    with open(file_path, "rb") as pickle_file:
        gfx = pickle.load(pickle_file)

    output_file_paths = GfxConverter.convert_and_export(
        gfx, common_options.converted_path / OUTPUT_GFX_DIR
    )

    typer.echo(f"Converted {file_path}")

    return output_file_paths


@app.command("sfx")
def convert_sfx(
    ctx: typer.Context,
    target_audio_format: TargetAudioFormat = typer.Option(
        default=TargetAudioFormat.WAV.value
    ),
    file_paths: Annotated[
        Optional[list[Path]], typer.Option(help=".sbf or .pickle files to convert.")
    ] = None,
) -> list[Path]:
    """Convert SFX files to WAV and MP3 files"""

    common_options: CommonOptions = ctx.obj
    audio_output_paths: list[Path] = []
    pickle_file_paths: list[Path] = []

    if not file_paths:
        pickle_file_paths = decode_sfx(ctx)

        decoded_sfx_path = common_options.decoded_path / SFX_DIR
        converted_sfx_path = common_options.converted_path / SFX_DIR

        for pickle_file_path in pickle_file_paths:
            typer.echo(f"Converting {pickle_file_path}...")

            with open(pickle_file_path, "rb") as pickle_file:
                sbf: Sbf = pickle.load(pickle_file)

            audio_output_path_parent = rebase_path(
                pickle_file_path.parent, decoded_sfx_path, converted_sfx_path
            )
            audio_output_paths = SbfConverter.convert_and_export(
                sbf, audio_output_path_parent, target_audio_format=target_audio_format
            )
            audio_output_paths.extend(audio_output_paths)

        return audio_output_paths

    for file_path in file_paths:
        if file_path.suffix == SBF_EXTENSION:
            pickle_file_paths.extend(decode_sfx(ctx, file_paths=[file_path]))
        elif file_path.suffix == PICKLE_EXTENSION:
            pickle_file_paths.append(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {file_path.suffix}")

    for pickle_file_path in pickle_file_paths:
        typer.echo(f"Converting {pickle_file_path}...")

        with open(pickle_file_path, "rb") as pickle_file:
            sbf = pickle.load(pickle_file)

        audio_output_paths = SbfConverter.convert_and_export(
            sbf, converted_sfx_path, target_audio_format=target_audio_format
        )
        audio_output_paths.extend(audio_output_paths)

    return audio_output_paths
