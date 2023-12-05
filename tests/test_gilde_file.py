import pytest

from europa1400_tools.models.gilde_file import GildeArchive, GildeAsset, GildeFile
from europa1400_tools.models.gilde_path import GildePath
from europa1400_tools.models.source_format import SourceFormat, SourceFormats


def test_init(game):
    path1 = GildePath("sample_file.bgf")
    file1 = GildeFile.from_path(path1)

    path2 = GildePath("animations.bin")
    file2 = GildeFile.from_path(path2)

    assert isinstance(file1, GildeAsset)
    assert isinstance(file2, GildeArchive)


def test_extracted_path(game):
    path1 = GildePath("sample_file.bgf")
    file1 = GildeFile.from_path(path1)

    path2 = GildePath("animations.bin")
    file2 = GildeFile.from_path(path2)

    assert file1.extracted_path == GildePath(
        "tests/output/extracted/objects/sample_file.bgf"
    )
    assert file2.extracted_path == GildePath("tests/output/extracted/animations")


def test_source_archive(game):
    path = GildePath("sample_file.bgf")
    file = GildeFile.from_path(path)

    assert isinstance(file, GildeAsset)

    assert file.source_archive == GildeArchive.from_path(GildePath("objects.bin"))


def test_extract_archive(game):
    file = GildeFile.from_path(GildePath("animations.bin"))

    assert isinstance(file, GildeArchive)

    extracted_assets = file.extract()

    asset1 = GildeAsset.from_path(GildePath("sample_file.baf"))
    asset2 = GildeAsset.from_path(GildePath("subdir/sample_file2.baf"))

    assert extracted_assets == [
        asset1,
        asset2,
    ]
    assert all(asset.extracted_path.exists() for asset in extracted_assets)


def test_extract_asset(game):
    asset = GildeAsset.from_path(GildePath("sample_file.bgf"))

    extracted_assets = asset.extract()

    assert len(extracted_assets) == 1
    assert extracted_assets[0] == asset
    assert extracted_assets[0].extracted_path.exists()


def test_asset_exists(game):
    file1 = GildePath("sample_file.bgf")
    file2 = GildePath("sample_file2.bgf")
    file3 = GildePath("sample_file.sbf")
    file4 = GildePath("tests/game/sfx/sample_file.sbf")
    file5 = GildePath("Data/A_Geb.dat")

    assert GildeAsset.exists(file1)
    assert GildeAsset.exists(file2)
    assert GildeAsset.exists(file3)
    assert GildeAsset.exists(file4)
    assert GildeAsset.exists(file5)


def test_asset_does_not_exist(game):
    file = GildePath("not.bgf")

    assert not GildeAsset.exists(file)


def test_asset_exists_no_format(game):
    file = GildePath("sample_file.not")

    assert not GildeAsset.exists(file)


def test_from_path(game):
    file1 = GildePath("sample_file.bgf")
    expected_file_1 = GildePath("sample_file.bgf")
    file2 = GildePath("sample_file2.bgf")
    expected_file_2 = GildePath("subdir/sample_file2.bgf")
    file3 = GildePath("sample_file.sbf")
    expected_file_3 = GildePath("sample_file.sbf")

    asset1 = GildeFile.from_path(file1)
    asset2 = GildeFile.from_path(file2)
    asset3 = GildeFile.from_path(file3)

    assert asset1.path == expected_file_1
    assert asset2.path == expected_file_2
    assert asset3.path == expected_file_3
    assert asset1.extracted_path.exists()
    assert asset2.extracted_path.exists()


def test_load_asset_exists(game):
    file1 = GildePath("Data/A_Geb.dat")
    file2 = GildePath("tests/game/Data/A_Geb.dat")

    asset1 = GildeFile.from_path(file1)
    asset2 = GildeFile.from_path(file2)

    assert asset1.path == GildePath("tests/game/Data/A_Geb.dat")
    assert asset1.extracted_path is None

    assert asset2.path == GildePath("tests/game/Data/A_Geb.dat")
    assert asset2.extracted_path is None


def test_load_asset_does_not_exist(game):
    file = GildePath("not.bgf")

    with pytest.raises(FileNotFoundError):
        GildeAsset.from_path(file)


def test_load_asset_no_format(game):
    file = GildePath("sample_file.not")

    with pytest.raises(NotImplementedError):
        GildeAsset.from_path(file)
