"""Commands for the decoder."""

import logging
import pickle
import time
from pathlib import Path
from typing import Annotated, Optional

import typer

from europa_1400_tools.const import (
    ANIMATIONS_BIN,
    BAF_EXTENSION,
    BGF_EXTENSION,
    ED3_EXTENSION,
    GROUPS_BIN,
    INI_EXTENSION,
    LFS_EXTENSION,
    OAM_EXTENSION,
    OBJECTS_BIN,
    OGR_EXTENSION,
    OUTPUT_AGEB_DIR,
    OUTPUT_ANIMATIONS_DIR,
    OUTPUT_AOBJ_DIR,
    OUTPUT_GFX_DIR,
    OUTPUT_GROUPS_DIR,
    OUTPUT_OBJECTS_DIR,
    OUTPUT_SCENES_DIR,
    OUTPUT_SFX_DIR,
    PICKLE_EXTENSION,
    SBF_EXTENSION,
    SCENES_BIN,
    TXS_EXTENSION,
)
from europa_1400_tools.construct.ageb import AGeb
from europa_1400_tools.construct.aobj import AObj
from europa_1400_tools.construct.baf import Baf, BafIni
from europa_1400_tools.construct.bgf import Bgf
from europa_1400_tools.construct.ed3 import Ed3
from europa_1400_tools.construct.gfx import Gfx
from europa_1400_tools.construct.ogr import Ogr
from europa_1400_tools.construct.sbf import Sbf
from europa_1400_tools.construct.txs import Txs
from europa_1400_tools.extractor.commands import extract
from europa_1400_tools.helpers import get_files, rebase_path
from europa_1400_tools.models import CommonOptions

app = typer.Typer()


@app.command("all")
def decode_all(ctx: typer.Context) -> None:
    """Decode all files."""

    decode_ageb(ctx)
    decode_aobj(ctx)
    cmd_decode_animations(ctx)
    decode_gfx(ctx)
    decode_groups(ctx)
    cmd_decode_objects(ctx)
    decode_scenes(ctx)
    decode_sfx(ctx)


@app.command("animations")
def cmd_decode_animations(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]],
        typer.Option("--file", "-f", help=".baf files to decode."),
    ] = None,
) -> list[Path]:
    """Command to decode BAF files."""

    common_options: CommonOptions = ctx.obj

    if not file_paths:
        animations_bin_path = common_options.game_resources_path / ANIMATIONS_BIN
        file_paths = extract(ctx, [animations_bin_path])

    if not file_paths:
        typer.echo("No files to decode.")
        return []

    return decode_animations(common_options, file_paths)


def decode_animations(
    common_options: CommonOptions,
    file_paths: list[Path],
) -> list[Path]:
    """Decode BAF files."""

    extracted_animations_path = common_options.extracted_path / OUTPUT_ANIMATIONS_DIR
    decoded_animations_path = common_options.decoded_path / OUTPUT_ANIMATIONS_DIR
    pickle_output_paths: list[Path] = []

    for file_path in file_paths:
        logging.debug(f"Decoding {file_path}...")

        if file_path.suffix == OAM_EXTENSION:
            continue

        if file_path.suffix.lower() == INI_EXTENSION:
            continue

        if file_path.suffix.lower() != BAF_EXTENSION:
            raise ValueError(f"Unknown file extension: {file_path.suffix}")

        baf = Baf.from_file(file_path)

        baf_ini_file_path = file_path.with_suffix(INI_EXTENSION)

        if baf_ini_file_path.exists():
            baf_ini_file = BafIni.from_file(baf_ini_file_path)
            baf.baf_ini = baf_ini_file

        pickle_output_path = rebase_path(
            file_path, extracted_animations_path, decoded_animations_path
        ).with_suffix(PICKLE_EXTENSION)

        if not pickle_output_path.parent.exists():
            pickle_output_path.parent.mkdir(parents=True)

        with open(pickle_output_path, "wb") as pickle_output_file:
            pickle.dump(
                baf,
                pickle_output_file,
            )

        pickle_output_paths.append(pickle_output_path)

    return pickle_output_paths


@app.command("objects")
def cmd_decode_objects(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]],
        typer.Option("--file", "-f", help=".bgf files to decode."),
    ] = None,
) -> list[Path]:
    """Command to decode BGF files."""

    common_options: CommonOptions = ctx.obj

    if not file_paths:
        objects_bin_path = common_options.game_resources_path / OBJECTS_BIN
        file_paths = extract(ctx, [objects_bin_path])

    if not file_paths:
        logging.warning("No files to decode.")
        return []

    return decode_objects(common_options, file_paths)


@app.command("txs")
def cmd_decode_txs(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]],
        typer.Option("--file", "-f", help=".txs files to decode."),
    ] = None,
) -> list[Path]:
    """Command to decode TXS files."""

    common_options: CommonOptions = ctx.obj

    if not file_paths:
        if common_options.extracted_objects_path.exists() and common_options.use_cache:
            file_paths = get_files(common_options.extracted_objects_path, TXS_EXTENSION)
        else:
            file_paths = extract(ctx, [common_options.game_objects_path])

    if not file_paths:
        logging.warning("No files to decode.")
        return []

    return decode_txs(common_options, file_paths)


def decode_objects(
    common_options: CommonOptions,
    file_paths: list[Path],
) -> list[Path]:
    """Decode BGF files."""

    extracted_objects_path = common_options.extracted_path / OUTPUT_OBJECTS_DIR
    decoded_objects_path = common_options.decoded_path / OUTPUT_OBJECTS_DIR
    pickle_output_paths: list[Path] = []

    for file_path in file_paths:
        logging.debug(f"Decoding {file_path}...")

        if file_path.suffix.lower() == TXS_EXTENSION:
            continue

        if file_path.suffix.lower() != BGF_EXTENSION:
            raise ValueError(f"Unknown file extension: {file_path.suffix}")

        bgf = Bgf.from_file(file_path)

        pickle_output_path = rebase_path(
            file_path, extracted_objects_path, decoded_objects_path
        ).with_suffix(PICKLE_EXTENSION)

        if not pickle_output_path.parent.exists():
            pickle_output_path.parent.mkdir(parents=True)

        with open(pickle_output_path, "wb") as pickle_output_file:
            pickle.dump(
                bgf,
                pickle_output_file,
            )

        pickle_output_paths.append(pickle_output_path)

    return pickle_output_paths


def decode_txs(
    common_options: CommonOptions,
    file_paths: list[Path],
) -> list[Path]:
    """Decode TXS files."""

    pickle_output_paths: list[Path] = []

    for file_path in file_paths:
        logging.debug(f"Decoding {file_path}...")

        if file_path.suffix.lower() == BGF_EXTENSION:
            continue

        if file_path.suffix.lower() != TXS_EXTENSION:
            raise ValueError(f"Unknown file extension: {file_path.suffix}")

        txs = Txs.from_file(file_path)

        pickle_output_path = rebase_path(
            file_path,
            common_options.extracted_objects_path,
            common_options.decoded_txs_path,
        ).with_suffix(PICKLE_EXTENSION)

        if not pickle_output_path.parent.exists():
            pickle_output_path.parent.mkdir(parents=True)

        with open(pickle_output_path, "wb") as pickle_output_file:
            pickle.dump(
                txs,
                pickle_output_file,
            )

        pickle_output_paths.append(pickle_output_path)

    return pickle_output_paths


@app.command("scenes")
def decode_scenes(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]],
        typer.Option("--file", "-f", help=".ed3 files to decode."),
    ] = None,
) -> list[Path]:
    """Decode ED3 files."""

    common_options: CommonOptions = ctx.obj
    scenes_bin_path = common_options.game_resources_path / SCENES_BIN
    extracted_scenes_path = common_options.extracted_path / OUTPUT_SCENES_DIR
    decoded_scenes_path = common_options.decoded_path / OUTPUT_SCENES_DIR
    pickle_output_paths: list[Path] = []

    if not file_paths:
        file_paths = extract(ctx, [scenes_bin_path])

    if not file_paths:
        logging.warning("No files to decode.")
        return []

    for file_path in file_paths:
        logging.debug(f"Decoding {file_path}...")

        if file_path.suffix == BGF_EXTENSION:
            continue

        if file_path.suffix != ED3_EXTENSION:
            raise ValueError(f"Unknown file extension: {file_path.suffix}")

        group = Ed3.from_file(file_path)

        pickle_output_path = rebase_path(
            file_path, extracted_scenes_path, decoded_scenes_path
        ).with_suffix(PICKLE_EXTENSION)

        if not pickle_output_path.parent.exists():
            pickle_output_path.parent.mkdir(parents=True)

        with open(pickle_output_path, "wb") as pickle_output_file:
            pickle.dump(
                group,
                pickle_output_file,
            )

        pickle_output_paths.append(pickle_output_path)

    return pickle_output_paths


@app.command("groups")
def decode_groups(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]],
        typer.Option("--file", "-f", help=".ogr files to decode."),
    ] = None,
) -> list[Path]:
    """Decode OGR files."""

    common_options: CommonOptions = ctx.obj
    groups_bin_path = common_options.game_resources_path / GROUPS_BIN
    extracted_groups_path = common_options.extracted_path / OUTPUT_GROUPS_DIR
    decoded_groups_path = common_options.decoded_path / OUTPUT_GROUPS_DIR
    pickle_output_paths: list[Path] = []

    if not file_paths:
        file_paths = extract(ctx, [groups_bin_path])

    for file_path in file_paths if file_paths else []:
        logging.debug(f"Decoding {file_path}...")

        if file_path.suffix == LFS_EXTENSION:
            logging.debug(f"Skipping LFS file: {file_path}")
            continue

        if file_path.suffix != OGR_EXTENSION:
            raise ValueError(f"Unknown file extension: {file_path.suffix}")

        group = Ogr.from_file(file_path)

        pickle_output_path = rebase_path(
            file_path, extracted_groups_path, decoded_groups_path
        ).with_suffix(PICKLE_EXTENSION)

        if not pickle_output_path.parent.exists():
            pickle_output_path.parent.mkdir(parents=True)

        with open(pickle_output_path, "wb") as pickle_output_file:
            pickle.dump(
                group,
                pickle_output_file,
            )

        pickle_output_paths.append(pickle_output_path)

    return pickle_output_paths


@app.command("ageb")
def decode_ageb(
    ctx: typer.Context,
) -> list[Path]:
    """Decode A_Geb file."""

    common_options: CommonOptions = ctx.obj
    decoded_ageb_path = common_options.decoded_path / OUTPUT_AGEB_DIR
    pickle_output_paths: list[Path] = []

    logging.debug(f"Decoding {common_options.game_ageb_path}...")

    ageb = AGeb.from_file(common_options.game_ageb_path)

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

    logging.debug(f"Decoding {common_options.game_aobj_path}...")

    aobj = AObj.from_file(common_options.game_aobj_path)

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
        file_path = common_options.game_gfx_path

    decode_time = time.time()
    logging.debug(f"Decoding {common_options.game_gfx_path}...")

    gfx = Gfx.from_file(file_path)

    logging.debug(f"Decoded {file_path} in {time.time() - decode_time:.2f} seconds.")

    dump_time = time.time()
    logging.debug("Dumping shapebanks...")

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
            logging.debug(f"Dumping {pickle_output_path}...")

        with open(pickle_output_path, "wb") as pickle_output_file:
            pickle.dump(
                shapebank_definition,
                pickle_output_file,
            )

        if common_options.verbose:
            logging.debug(
                f"Dumped {pickle_output_path} in "
                + f"{time.time() - dump_shapebank_time:.2f} seconds."
            )

        pickle_output_paths.append(pickle_output_path)

    logging.debug(f"Dumped shapebanks in {time.time() - dump_time:.2f} seconds.")

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
        file_paths = get_files(common_options.game_sfx_path, SBF_EXTENSION)

        for file in file_paths if file_paths else []:
            logging.debug(f"Decoding {file}...")

            sbf = Sbf.from_file(file)
            pickle_output_path = rebase_path(
                file, common_options.game_sfx_path, decoded_sfx_path
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
        logging.debug(f"Decoding {file}...")

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
