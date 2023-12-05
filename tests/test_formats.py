from dataclasses import dataclass
from pathlib import Path

from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.cli.convert_options import ConvertOptions
from europa1400_tools.cli.file_options import FileOptions
from europa1400_tools.models.gilde_path import GildePath
from europa1400_tools.models.source_format import SourceFormat, SourceFormats


def test_source_format_from_path(game, convert_options: ConvertOptions):
    paths_to_source_formats: dict[Path, SourceFormats] = {
        GildePath("sample_file.bgf"): SourceFormats.BGF,
        GildePath("Data/A_Geb.dat"): SourceFormats.AGEB,
        GildePath("A_Obj.dat"): SourceFormats.AOBJ,
        GildePath("Resources/animations.bin"): SourceFormats.BAF,
        GildePath("test.BGF.pickle"): SourceFormats.BGF,
        GildePath("some_file.ed3"): SourceFormats.ED3,
        GildePath("sfx"): SourceFormats.SBF,
        GildePath("forms.bin0"): SourceFormats.FORM,
    }

    for path, source_format in paths_to_source_formats.items():
        actual_source_format = SourceFormat.from_path(path)
        assert actual_source_format == source_format.value


def test_source_format_real_game(real_game):
    paths_to_source_formats: dict[Path, SourceFormats] = {
        GildePath("Locations/Geldleihe_Arbeitsraum/zoom_out_ANTEIL"): SourceFormats.ESC,
        GildePath(
            "output/extracted/scripts/Locations/Geldleihe_Arbeitsraum/zoom_out_ANTEIL"
        ): SourceFormats.ESC,
    }

    for path, source_format in paths_to_source_formats.items():
        actual_source_format = SourceFormat.from_path(path)
        assert actual_source_format == source_format.value
