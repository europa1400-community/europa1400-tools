import timeit

from europa1400_tools.models.gilde_file import GildeArchive, GildeAsset
from europa1400_tools.models.gilde_path import GildePath
from europa1400_tools.models.source_format import SourceFormats


def test_benchmark_gilde_path(game: None):
    path = GildePath("tests/game/Resources/objects.bin")
    path2 = GildePath("sample_file.bgf")
    archive = GildeArchive(path, SourceFormats.BGF.value)
    asset = GildeAsset(path2, SourceFormats.BGF.value)

    timer = timeit.default_timer()

    for _ in range(1000):
        a = path.has_suffix(".bin")

    time1 = timeit.default_timer() - timer

    for _ in range(1000):
        a = asset.source_path.is_archive

    time2 = timeit.default_timer() - timer

    for _ in range(1000):
        a = asset.extracted_path.exists()

    time3 = timeit.default_timer() - timer

    for _ in range(1000):
        a = path.is_archive

    time4 = timeit.default_timer() - timer

    pass
