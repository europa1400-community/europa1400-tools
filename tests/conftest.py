from pathlib import Path
from zipfile import ZipFile

import pytest
from typer.testing import CliRunner

from europa1400_tools.__main__ import app as typer_app
from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.cli.convert_options import ConvertOptions
from europa1400_tools.cli.file_options import FileOptions
from europa1400_tools.const import (
    BIN_FILES,
    DATA_DIR,
    GAME_A_GEB_DAT,
    GAME_A_OBJ_DAT,
    GAME_RESOURCES_OBJECTS_BIN_PATH,
    GAME_RESOURCES_SCRIPTS_BIN_PATH,
    GFX_DIR,
    RESOURCES_DIR,
    SFX_DIR,
)
from europa1400_tools.models.gilde_path import GildePath
from europa1400_tools.models.source_format import SourceFormat, SourceFormats


@pytest.fixture(scope="session")
def real_game(common_options: CommonOptions):
    # Create game directory

    resources_dir = common_options.game_path / RESOURCES_DIR
    resources_dir.mkdir(parents=True, exist_ok=True)

    scripts_bin = common_options.game_path / GAME_RESOURCES_SCRIPTS_BIN_PATH

    archived_files = [GildePath("Locations/Geldleihe_Arbeitsraum/zoom_out_ANTEIL")]

    with ZipFile(scripts_bin, "w") as zip_file:
        for archived_file in archived_files:
            zip_file.writestr(archived_file.as_posix(), "sample content")


@pytest.fixture(scope="session")
def game(common_options: CommonOptions):
    # Create game directory

    resources_dir = common_options.game_path / RESOURCES_DIR
    resources_dir.mkdir(parents=True, exist_ok=True)

    for bin_file in BIN_FILES:
        bin_file = common_options.game_path / bin_file
        source_format = SourceFormat.from_path(bin_file)

        archived_files = [
            GildePath("sample_file").with_suffix(source_format.suffix),
            GildePath("subdir/sample_file2").with_suffix(source_format.suffix),
        ]

        with ZipFile(bin_file, "w") as zip_file:
            for archived_file in archived_files:
                zip_file.writestr(archived_file.as_posix(), "sample content")

    sfx_dir = common_options.game_path / SFX_DIR
    gfx_dir = common_options.game_path / GFX_DIR

    sfx_dir.mkdir(parents=True, exist_ok=True)
    gfx_dir.mkdir(parents=True, exist_ok=True)

    sample_sbf_file_1 = sfx_dir / "sample_file.sbf"
    sample_sbf_file_2 = sfx_dir / "subdir" / "sample_file2.sbf"
    sample_sbf_file_1.write_text("sample content")
    sample_sbf_file_2.parent.mkdir(parents=True, exist_ok=True)
    sample_sbf_file_2.write_text("sample content")

    sample_gfx_file = gfx_dir / "sample_file.gfx"
    sample_gfx_file.write_text("sample content")

    data_dir = common_options.game_path / DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)

    ageb_file = data_dir / GAME_A_GEB_DAT
    ageb_file.write_text("sample content")

    aobj_file = data_dir / GAME_A_OBJ_DAT
    aobj_file.write_text("sample content")


@pytest.fixture(scope="session")
def common_options():
    common_options = CommonOptions()
    common_options.game_path = GildePath("tests/game")
    common_options.output_path = GildePath("tests/output")

    return common_options


@pytest.fixture(scope="session")
def file_options():
    file_options = FileOptions()

    return file_options


@pytest.fixture(scope="session")
def convert_options():
    convert_options = ConvertOptions()

    return convert_options


@pytest.fixture(scope="session")
def cli():
    runner = CliRunner()

    return runner


@pytest.fixture(scope="session")
def app():
    return typer_app
