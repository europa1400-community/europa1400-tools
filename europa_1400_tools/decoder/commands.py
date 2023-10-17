"""Commands for the decoder."""

from pathlib import Path
from typing import Annotated, Optional

import typer

from europa_1400_tools.common_options import CommonOptions
from europa_1400_tools.decoder.ageb_decoder import AGebDecoder
from europa_1400_tools.decoder.aobj_decoder import AObjDecoder
from europa_1400_tools.decoder.baf_decoder import BafDecoder
from europa_1400_tools.decoder.bgf_decoder import BgfDecoder
from europa_1400_tools.decoder.ed3_decoder import Ed3Decoder
from europa_1400_tools.decoder.gfx_decoder import GfxDecoder
from europa_1400_tools.decoder.ogr_decoder import OgrDecoder
from europa_1400_tools.decoder.sbf_decoder import SbfDecoder
from europa_1400_tools.decoder.txs_decoder import TxsDecoder

app = typer.Typer()


@app.command("all")
def decode_all(ctx: typer.Context) -> None:
    """Decode all files."""

    cmd_decode_ageb(ctx)
    cmd_decode_aobj(ctx)
    cmd_decode_sfx(ctx)
    cmd_decode_gfx(ctx)
    cmd_decode_objects(ctx)
    cmd_decode_animations(ctx)
    cmd_decode_groups(ctx)
    cmd_decode_scenes(ctx)


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

    baf_decoder = BafDecoder(common_options)
    baf_decoder.decode_files(file_paths)


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

    bgf_decoder = BgfDecoder(common_options)
    bgf_decoder.decode_files(file_paths)


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

    txs_decoder = TxsDecoder(common_options)
    txs_decoder.decode_files(file_paths)


@app.command("scenes")
def cmd_decode_scenes(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]],
        typer.Option("--file", "-f", help=".ed3 files to decode."),
    ] = None,
) -> list[Path]:
    """Decode ED3 files."""

    common_options: CommonOptions = ctx.obj

    ed3_decoder = Ed3Decoder(common_options)
    ed3_decoder.decode_files(file_paths)


@app.command("groups")
def cmd_decode_groups(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]],
        typer.Option("--file", "-f", help=".ogr files to decode."),
    ] = None,
):
    """Decode OGR files."""

    common_options: CommonOptions = ctx.obj

    ogr_decoder = OgrDecoder(common_options)
    ogr_decoder.decode_files(file_paths)


@app.command("ageb")
def cmd_decode_ageb(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]],
        typer.Option("--file", "-f", help="A_Geb files to decode."),
    ] = None,
):
    """Decode A_Geb file."""

    common_options: CommonOptions = ctx.obj

    ageb_decoder = AGebDecoder(common_options)
    ageb_decoder.decode_files(file_paths)


@app.command("aobj")
def cmd_decode_aobj(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]],
        typer.Option("--file", "-f", help="A_Obj files to decode."),
    ] = None,
) -> list[Path]:
    """Decode A_Obj file."""

    common_options: CommonOptions = ctx.obj

    aobj_decoder = AObjDecoder(common_options)
    aobj_decoder.decode_files(file_paths)


@app.command("gfx")
def cmd_decode_gfx(
    ctx: typer.Context,
    file_path: Annotated[
        Optional[Path], typer.Option("--file", "-f", help=".gfx file to decode.")
    ] = None,
) -> list[Path]:
    """Decode GFX file."""

    common_options: CommonOptions = ctx.obj

    gfx_decoder = GfxDecoder(common_options)
    gfx_decoder.decode_files(file_path)


@app.command("sfx")
def cmd_decode_sfx(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]], typer.Option("--file", "-f", help=".sbf files to decode.")
    ] = None,
) -> list[Path]:
    """Decode SFX files."""

    common_options: CommonOptions = ctx.obj

    sbf_decoder = SbfDecoder(common_options)
    sbf_decoder.decode_files(file_paths)
