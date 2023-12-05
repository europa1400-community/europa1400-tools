from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.cli.convert_options import ConvertOptions
from europa1400_tools.cli.file_options import FileOptions
from europa1400_tools.models.gilde_path import GildePath
from europa1400_tools.models.target_format import TargetFormats


def test_options():
    common_options = CommonOptions()
    common_options.game_path = "tests/game"
    common_options.output_path = "tests/output"

    file_options = FileOptions()
    file_options.file_paths = [GildePath("tests/game/Resources/objects.bin")]

    convert_options = ConvertOptions()
    convert_options.target_format = TargetFormats.JSON.value

    assert CommonOptions.instance == common_options
    assert FileOptions.instance == file_options
    assert ConvertOptions.instance == convert_options
    assert CommonOptions.ATTRNAME == "CommonOptions"
    assert FileOptions.ATTRNAME == "FileOptions"
    assert ConvertOptions.ATTRNAME == "ConvertOptions"
