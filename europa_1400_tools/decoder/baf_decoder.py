from pathlib import Path

from europa_1400_tools.cli.common_options import CommonOptions
from europa_1400_tools.const import BAF_EXTENSION, INI_EXTENSION
from europa_1400_tools.construct.baf import Baf, BafIni
from europa_1400_tools.decoder.base_decoder import BaseDecoder


class BafDecoder(BaseDecoder[Baf]):
    """Decoder for BAF files."""

    def __init__(self):
        super().__init__(Baf)

    def decode_file(self, file_path: Path) -> Baf:
        baf = Baf.from_file(file_path)

        baf_ini_file_path = file_path.with_suffix(INI_EXTENSION)

        if baf_ini_file_path.exists():
            baf_ini_file = BafIni.from_file(baf_ini_file_path)
            baf.baf_ini = baf_ini_file

        return baf

    @property
    def file_suffix(self) -> str:
        return BAF_EXTENSION

    @property
    def is_archive(self) -> bool:
        return True

    @property
    def is_single_file(self) -> bool:
        return False

    @property
    def game_path(self) -> Path:
        return CommonOptions.instance.game_animations_path

    @property
    def extracted_path(self) -> Path | None:
        return CommonOptions.instance.extracted_animations_path

    @property
    def decoded_path(self) -> Path:
        return CommonOptions.instance.decoded_animations_path
