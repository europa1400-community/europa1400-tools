import typer

from europa1400_tools.cli.command import callback
from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.cli.file_options import FileOptions
from europa1400_tools.const import BIN_FILES
from europa1400_tools.extractor.file_extractor import FileExtractor
from europa1400_tools.models.gilde_file import GildeAsset, GildeFile
from europa1400_tools.models.gilde_path import GildePath
from europa1400_tools.models.source_format import SourceFormats

app = typer.Typer()


@callback(app, [CommonOptions, FileOptions], invoke_without_command=True)
def extract(
    ctx: typer.Context,
):
    """Extract files."""

    if not FileOptions.instance.files:
        source_paths: set[GildePath] = set()

        for source_format in SourceFormats:
            for source_path in source_format.value.source_paths:
                source_paths.add(source_path)

        FileOptions.instance.files = GildeFile.from_paths(source_paths)

    extractor = FileExtractor()
    extractor.extract(FileOptions.instance.files)
