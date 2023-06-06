"""Commands for converting files"""

import pickle
import time
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
from europa_1400_tools.construct.gfx import ShapebankDefinition
from europa_1400_tools.construct.sbf import Sbf
from europa_1400_tools.converter.sbf_converter import SbfConverter
from europa_1400_tools.converter.shapebank_converter import ShapebankConverter
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
    file_paths: Annotated[
        Optional[list[Path]],
        typer.Option("--file", "-f", help=".gfx file or .pickle files to convert."),
    ] = None,
) -> list[Path]:
    """Convert GFX file to PNG files"""

    common_options: CommonOptions = ctx.obj
    output_file_paths: list[Path] = []

    if not file_paths:
        file_paths = [common_options.gfx_game_path]

    # check for mixed extensions
    if not all(file_path.suffix == file_paths[0].suffix for file_path in file_paths):
        raise ValueError("All files must have the same extension")

    suffix = file_paths[0].suffix

    if suffix not in [GFX_EXTENSION, PICKLE_EXTENSION]:
        raise ValueError(f"Unknown file extension: {suffix}")

    is_gfx: bool = suffix == GFX_EXTENSION

    if is_gfx and len(file_paths) > 1:
        raise ValueError("Can only convert one .gfx file at a time")

    if is_gfx:
        file_paths = decode_gfx(ctx, file_paths[0])

    shapebank_definitions: list[ShapebankDefinition] = []

    load_time = time.time()
    typer.echo(f"Loading {len(file_paths)} files...")

    for file_path in file_paths:
        load_shapebank_time = time.time()

        with open(file_path, "rb") as pickle_file:
            shapebank_definition: ShapebankDefinition = pickle.load(pickle_file)

        if common_options.verbose:
            typer.echo(
                f"Loaded {shapebank_definition.name} in "
                + f"{time.time() - load_shapebank_time:.2f}s"
            )

        shapebank_definitions.append(shapebank_definition)

    typer.echo(f"Loaded {len(file_paths)} files in {time.time() - load_time:.2f}s")

    convert_time = time.time()
    typer.echo(f"Converting {len(file_paths)} files...")

    for shapebank_definition in shapebank_definitions:
        convert_shapebank_time = time.time()

        output_file_paths = ShapebankConverter.convert_and_export(
            shapebank_definition, common_options.converted_path / OUTPUT_GFX_DIR
        )

        if common_options.verbose:
            typer.echo(
                f"Converted {shapebank_definition.name} in "
                + f"{time.time() - convert_shapebank_time:.2f}s"
            )

    typer.echo(
        f"Converted {len(file_paths)} files in {time.time() - convert_time:.2f}s"
    )

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
