"""Common objects and functions for europa1400_tools."""

import sys

import typer

from europa1400_tools.cli.command import callback
from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.converter.commands import app as convert_app
from europa1400_tools.decoder.commands import app as decode_app
from europa1400_tools.extractor.commands import app as extract_app
from europa1400_tools.preprocessor.commands import app as preprocess_app

# app.add_typer(extract_app, name="extract")
# app.add_typer(decode_app, name="decode")
app = typer.Typer()
app.add_typer(
    convert_app,
    name="convert",
)
app.add_typer(preprocess_app, name="preprocess")


@callback(app, CommonOptions)
def main(
    ctx: typer.Context,
) -> None:
    """Main entry point."""

    if "--help" in sys.argv:
        return
