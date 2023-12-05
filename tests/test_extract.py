from typer import Typer
from typer.testing import CliRunner

from europa1400_tools.cli.file_options import FileOptions
from europa1400_tools.extractor.file_extractor import FileExtractor
from europa1400_tools.models.gilde_file import GildeFile
from europa1400_tools.models.gilde_path import GildePath


def test_file_extractor(game: None):
    assets = [
        GildeFile.from_path(GildePath("tests/game/Resources/objects.bin")),
        GildeFile.from_path(GildePath("subdir/sample_file2.baf")),
    ]

    extracted_assets = FileExtractor().extract(assets)

    assert len(extracted_assets) == 3


def test_extract(game: None, cli: CliRunner, app: Typer):
    path = GildePath("tests/game/Resources/objects.bin")

    result = cli.invoke(app, ["extract", path.as_posix()])

    assert result.exit_code == 0
