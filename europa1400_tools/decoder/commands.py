"""Commands for the decoder."""

from pathlib import Path
from typing import Annotated, Optional

import typer

from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.decoder.ageb_decoder import AGebDecoder
from europa1400_tools.decoder.aobj_decoder import AObjDecoder
from europa1400_tools.decoder.baf_decoder import BafDecoder
from europa1400_tools.decoder.bgf_decoder import BgfDecoder
from europa1400_tools.decoder.ed3_decoder import Ed3Decoder
from europa1400_tools.decoder.gfx_decoder import GfxDecoder
from europa1400_tools.decoder.ogr_decoder import OgrDecoder
from europa1400_tools.decoder.sbf_decoder import SbfDecoder
from europa1400_tools.decoder.txs_decoder import TxsDecoder

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
):
    """Command to decode BAF files."""

    baf_decoder = BafDecoder()
    baf_decoder.decode_files(file_paths)


@app.command("objects")
def cmd_decode_objects(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]],
        typer.Option("--file", "-f", help=".bgf files to decode."),
    ] = None,
):
    """Command to decode BGF files."""

    bgf_decoder = BgfDecoder()
    bgf_decoder.decode_files(file_paths)


@app.command("txs")
def cmd_decode_txs(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]],
        typer.Option("--file", "-f", help=".txs files to decode."),
    ] = None,
):
    """Command to decode TXS files."""

    txs_decoder = TxsDecoder()
    txs_decoder.decode_files(file_paths)


@app.command("scenes")
def cmd_decode_scenes(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]],
        typer.Option("--file", "-f", help=".ed3 files to decode."),
    ] = None,
):
    """Decode ED3 files."""

    ed3_decoder = Ed3Decoder()
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

    ogr_decoder = OgrDecoder()
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

    ageb_decoder = AGebDecoder()
    ageb_decoder.decode_files(file_paths)


@app.command("aobj")
def cmd_decode_aobj(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]],
        typer.Option("--file", "-f", help="A_Obj files to decode."),
    ] = None,
):
    """Decode A_Obj file."""

    aobj_decoder = AObjDecoder()
    aobj_decoder.decode_files(file_paths)


@app.command("gfx")
def cmd_decode_gfx(
    ctx: typer.Context,
    file_path: Annotated[
        Optional[list[Path]], typer.Option("--file", "-f", help=".gfx file to decode.")
    ] = None,
):
    """Decode GFX file."""

    gfx_decoder = GfxDecoder()
    gfx_decoder.decode_files(file_path)


@app.command("sfx")
def cmd_decode_sfx(
    ctx: typer.Context,
    file_paths: Annotated[
        Optional[list[Path]], typer.Option("--file", "-f", help=".sbf files to decode.")
    ] = None,
):
    """Decode SFX files."""

    sbf_decoder = SbfDecoder()
    sbf_decoder.decode_files(file_paths)
