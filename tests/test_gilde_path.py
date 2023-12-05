import pytest

from europa1400_tools.models.gilde_path import GildePath

# Sample test data
test_file = GildePath("sample_file.bin")


def test_has_suffix():
    assert test_file.has_suffix("bin")  # Should return True
    assert not test_file.has_suffix("txt")  # Should return False


def test_is_archive():
    assert test_file.is_archive  # Should return True
    non_archive_file = GildePath("sample_file.txt")
    assert not non_archive_file.is_archive  # Should return False


def test_equality():
    assert test_file == "sample_file.bin"  # Should return True
    assert test_file == GildePath("sample_file.bin")  # Should return True
    assert not test_file == "other_file.bin"  # Should return False
    assert not test_file == GildePath("other_file.bin")  # Should return False


def test_invalid_input():
    with pytest.raises(NotImplementedError):
        test_file == 42  # Invalid input should raise NotImplementedError


def test_dir_find(game):
    parent = GildePath("tests/game/sfx")
    file1 = GildePath("sample_file.sbf")
    file2 = GildePath("sample_file2.sbf")
    expected_file2 = GildePath("subdir/sample_file2.sbf")
    file3 = GildePath("tests/game/sfx/sample_file.sbf")
    expected_file3 = GildePath("sample_file.sbf")

    assert parent.find(file1) == file1
    assert parent.find(file2) == expected_file2
    assert parent.find(file3) == expected_file3
    assert parent.resolve().find(file3) == expected_file3


def test_archive_find(game):
    parent = GildePath("tests/game/Resources/objects.bin")
    file1 = GildePath("sample_file.bgf")
    file2 = GildePath("sample_file2.bgf")
    expected_file2 = GildePath("subdir/sample_file2.bgf")

    assert parent.find(file1) == file1
    assert parent.resolve().find(file1) == file1
    assert parent.find(file2) == expected_file2
    assert parent.resolve().find(file2) == expected_file2


def test_archive_contains(game):
    archive = GildePath("tests/game/Resources/objects.bin")
    file1 = GildePath("sample_file.bgf")
    file2 = GildePath("sample_file2.bgf")
    file3 = GildePath("subdir/sample_file2.bgf")

    assert archive.contains(file1)
    assert archive.contains(file2)
    assert archive.contains(file3)


def test_file_contains(game):
    file = GildePath("tests/game/sfx/sample_file.sbf")
    file2 = GildePath("tests/game/sfx/subdir/sample_file2.sbf")

    assert not file.contains(file2)
    assert file.contains(file)


def test_contained(game):
    path1 = GildePath("tests/game/sfx")
    path2 = GildePath("tests/game/Resources/objects.bin")

    expected_paths1 = [
        GildePath("sample_file.sbf"),
        GildePath("subdir/sample_file2.sbf"),
    ]

    expected_paths2 = [
        GildePath("sample_file.bgf"),
        GildePath("subdir/sample_file2.bgf"),
    ]

    assert len(path1.contained) == len(expected_paths1)
    assert len(path2.contained) == len(expected_paths2)
    assert path1.contained == expected_paths1
    assert path2.contained == expected_paths2


def test_find_not_existing(game):
    archive = GildePath("tests/game/Resources/objects.bin")
    directory = GildePath("tests/game/sfx")
    file = GildePath("tests/game/sfx/does_not_exist.sbf")
    file2 = GildePath("does_not_exist.bgf")

    assert archive.find(file) is None
    assert directory.find(file2) is None


def test_find_in_file(game):
    file = GildePath("tests/game/sfx/sample_file.sbf")
    file2 = GildePath("foo.sbf")

    assert file.find(file2) is None


def test_extract(game):
    archive = GildePath("tests/game/Resources/objects.bin")
    file1 = GildePath("sample_file.bgf")
    expected_file1 = GildePath("sample_file.bgf")
    file2 = GildePath("subdir/sample_file2.bgf")
    expected_file2 = GildePath("subdir/sample_file2.bgf")

    assert (
        archive.extract(file1, GildePath("tests/output/extracted/objects"))
        == expected_file1
    )
    assert (
        archive.extract(file2, GildePath("tests/output/extracted/objects"))
        == expected_file2
    )


def test_extract_non_existing(game):
    archive = GildePath("tests/game/Resources/objects.bin")
    non_existing_file = GildePath("does_not_exist.bgf")

    with pytest.raises(FileNotFoundError):
        archive.extract(non_existing_file, GildePath("tests/output/extracted/objects"))


def test_extract_all(game):
    archive = GildePath("tests/game/Resources/objects.bin")

    expected_paths = [
        GildePath("sample_file.bgf"),
        GildePath("subdir/sample_file2.bgf"),
    ]

    actual_paths = archive.extract_all(GildePath("tests/output/extracted/objects"))

    for expected_path in expected_paths:
        assert expected_path in actual_paths


def test_equals(game):
    path: GildePath | None = None
    assert GildePath("abc.def") != path


def test_repr(game):
    path = GildePath("SOME_Dir/abc.def")
    assert repr(path) == "GildePath('SOME_Dir/abc.def')"


def test_rebase():
    old_base = GildePath("tests/game")
    new_base = GildePath("tests/output")

    path = GildePath("tests/game/sfx/sample_file.sbf")
    expected_path = GildePath("tests/output/sfx/sample_file.sbf")

    assert path.rebase(old_base, new_base) == expected_path


def test_rebase_not_relative():
    old_base = GildePath("tests/game")
    new_base = GildePath("tests/output")

    path = GildePath("tests/output/sample_file.sbf")

    with pytest.raises(ValueError):
        path.rebase(old_base, new_base)


def test_rebase_absolute():
    old_base = GildePath("tests/game")
    new_base = GildePath("tests/output")

    path = GildePath("tests/game/sfx/sample_file.sbf")
    expected_path = GildePath("tests/output/sfx/sample_file.sbf")

    assert path.resolve().rebase(old_base, new_base) == expected_path.resolve()


def test_parent():
    path_to_parent = {
        GildePath("does/not/exist/sample_file.sbf"): GildePath("does/not/exist"),
        GildePath("does/not/exist"): GildePath("does/not"),
        GildePath("does/not"): GildePath("does"),
        GildePath("does"): GildePath("."),
        GildePath("."): GildePath("."),
        GildePath("/"): GildePath("/"),
    }

    for path, parent in path_to_parent.items():
        assert path.parent == parent


# def test_gilde_file(
#     common_options: CommonOptions,
#     convert_options: ConvertOptions,
#     file_options: FileOptions,
# ):
#     @dataclass
#     class GildeFileTestCase:
#         path: Path
#         source_format: SourceFormat
#         relative_path: Path
#         extracted_path: Path
#         decoded_path: Path
#         converted_path: Path
#         source_paths: Path
#         is_archive: bool

#     test_cases = [
#         GildeFileTestCase(
#             Path("tests/output/extracted/scenes/subdir/some_file.ed3"),
#             SourceFormats.ED3.value,
#             Path("subdir/some_file.ed3"),
#             Path("tests/output/extracted/scenes/subdir/some_file.ed3").resolve(),
#             Path("tests/output/decoded/scenes/subdir/some_file.ed3.pickle").resolve(),
#             Path("tests/output/converted/scenes/subdir/some_file.json").resolve(),
#             [Path("tests/game/Resources/scenes.bin").resolve()],
#             False,
#         ),
#         GildeFileTestCase(
#             Path("subdir/some_file.gfx"),
#             SourceFormats.GFX.value,
#             Path("some_file.gfx"),
#             None,
#             Path("tests/output/decoded/gfx/some_file.gfx.pickle").resolve(),
#             Path("tests/output/converted/gfx/").resolve(),
#             [Path("tests/game/gfx").resolve()],
#             False,
#         ),
#         GildeFileTestCase(
#             Path("A_Geb.dat"),
#             SourceFormats.AGEB.value,
#             Path("A_Geb.dat"),
#             None,
#             Path("tests/output/decoded/A_Geb.dat.pickle").resolve(),
#             Path("tests/output/converted/ageb.json").resolve(),
#             [Path("tests/game/Data/A_Geb.dat").resolve()],
#             False,
#         ),
#         GildeFileTestCase(
#             Path("some_file.sbf"),
#             SourceFormats.SBF.value,
#             Path("some_file.sbf"),
#             None,
#             Path("tests/output/decoded/sfx/some_file.sbf.pickle").resolve(),
#             Path("tests/output/converted/sfx/wav/some_file/").resolve(),
#             [Path("tests/game/sfx").resolve()],
#             False,
#         ),
#         GildeFileTestCase(
#             Path("objects.bin"),
#             SourceFormats.BGF.value,
#             Path("objects.bin"),
#             Path("tests/output/extracted/objects").resolve(),
#             Path("tests/output/decoded/objects").resolve(),
#             Path("tests/output/converted/objects/wavefront").resolve(),
#             [Path("tests/game/Resources/objects.bin").resolve()],
#             True,
#         ),
#     ]

#     file_options.file_paths = [test_case.path for test_case in test_cases]

#     assert len(file_options.gilde_files) == len(test_cases)

#     for gilde_file, test_case in zip(file_options.gilde_files, test_cases):
#         assert gilde_file.source_format == test_case.source_format
#         assert gilde_file.path == test_case.relative_path
#         assert gilde_file.extracted_path == test_case.extracted_path
#         assert gilde_file.decoded_path == test_case.decoded_path
#         assert gilde_file.converted_path == test_case.converted_path
#         assert gilde_file.source_paths == test_case.source_paths
#         assert gilde_file.is_archive == test_case.is_archive


# def test_gilde_file_path():
#     test_cases = {
#         Path(): Path(),
#     }

#     for input_path, expected_path in test_cases.items():
#         actual_path = GildePath._get_relative_path(input_path)
#         assert actual_path == expected_path
