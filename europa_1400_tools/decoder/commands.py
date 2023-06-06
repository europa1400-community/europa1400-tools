"""Commands for the decoder."""

import pickle
import time
from pathlib import Path
from typing import Annotated, Optional

import typer

from europa_1400_tools.const import (
    OUTPUT_AGEB_DIR,
    OUTPUT_AOBJ_DIR,
    OUTPUT_GFX_DIR,
    OUTPUT_SFX_DIR,
    PICKLE_EXTENSION,
    SBF_EXTENSION,
)
from europa_1400_tools.construct.ageb import AGeb
from europa_1400_tools.construct.aobj import AObj
from europa_1400_tools.construct.gfx import Gfx
from europa_1400_tools.construct.sbf import Sbf
from europa_1400_tools.helpers import get_files, rebase_path
from europa_1400_tools.models import CommonOptions

app = typer.Typer()


@app.command("all")
def decode_all() -> None:
    """Decode all files."""

    raise NotImplementedError()


@app.command("ageb")
def decode_ageb(
    ctx: typer.Context,
) -> list[Path]:
    """Decode A_Geb file."""

    common_options: CommonOptions = ctx.obj
    decoded_ageb_path = common_options.decoded_path / OUTPUT_AGEB_DIR
    pickle_output_paths: list[Path] = []

    typer.echo(f"Decoding {common_options.ageb_game_path}...")

    ageb = AGeb.from_file(common_options.ageb_game_path)

    for building in ageb.buildings:
        pickle_output_path = decoded_ageb_path / Path(building.name).with_suffix(
            PICKLE_EXTENSION
        )

        if not pickle_output_path.parent.exists():
            pickle_output_path.parent.mkdir(parents=True)

        with open(pickle_output_path, "wb") as pickle_output_file:
            pickle.dump(
                building,
                pickle_output_file,
            )

        pickle_output_paths.append(pickle_output_path)

    return pickle_output_paths


@app.command("aobj")
def decode_aobj(
    ctx: typer.Context,
) -> list[Path]:
    """Decode A_Obj file."""

    common_options: CommonOptions = ctx.obj
    decoded_aobj_path = common_options.decoded_path / OUTPUT_AOBJ_DIR
    pickle_output_paths: list[Path] = []

    typer.echo(f"Decoding {common_options.aobj_game_path}...")

    aobj = AObj.from_file(common_options.aobj_game_path)

    for object_data in aobj.objects:
        pickle_output_path = decoded_aobj_path / Path(object_data.name).with_suffix(
            PICKLE_EXTENSION
        )

        if not pickle_output_path.parent.exists():
            pickle_output_path.parent.mkdir(parents=True)

        with open(pickle_output_path, "wb") as pickle_output_file:
            pickle.dump(
                object_data,
                pickle_output_file,
            )

        pickle_output_paths.append(pickle_output_path)

    return pickle_output_paths


@app.command("gfx")
def decode_gfx(
    ctx: typer.Context,
    file_path: Annotated[
        Optional[Path], typer.Option("--file", "-f", help=".gfx file to decode.")
    ] = None,
) -> list[Path]:
    """Decode GFX file."""

    common_options: CommonOptions = ctx.obj
    decoded_gfx_path = common_options.decoded_path / OUTPUT_GFX_DIR
    pickle_output_paths: list[Path] = []

    if not file_path:
        file_path = common_options.gfx_game_path

    decode_time = time.time()
    typer.echo(f"Decoding {common_options.gfx_game_path}...")

    gfx = Gfx.from_file(file_path)

    typer.echo(f"Decoded {file_path} in {time.time() - decode_time:.2f} seconds.")

    dump_time = time.time()
    typer.echo("Dumping shapebanks...")

    for shapebank_definition in gfx.shapebank_definitions:
        if not shapebank_definition.shapebank:
            continue

        pickle_output_path = decoded_gfx_path / Path(
            shapebank_definition.name
        ).with_suffix(PICKLE_EXTENSION)

        if not pickle_output_path.parent.exists():
            pickle_output_path.parent.mkdir(parents=True)

        dump_shapebank_time = time.time()
        if common_options.verbose:
            typer.echo(f"Dumping {pickle_output_path}...")

        with open(pickle_output_path, "wb") as pickle_output_file:
            pickle.dump(
                shapebank_definition,
                pickle_output_file,
            )

        if common_options.verbose:
            typer.echo(
                f"Dumped {pickle_output_path} in "
                + f"{time.time() - dump_shapebank_time:.2f} seconds."
            )

        pickle_output_paths.append(pickle_output_path)

    typer.echo(f"Dumped shapebanks in {time.time() - dump_time:.2f} seconds.")

    return pickle_output_paths


@app.command("sfx")
def decode_sfx(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]], typer.Option("--file", "-f", help=".sbf files to decode.")
    ] = None,
) -> list[Path]:
    """Decode SFX files."""

    common_options: CommonOptions = ctx.obj
    decoded_sfx_path = common_options.decoded_path / OUTPUT_SFX_DIR
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
