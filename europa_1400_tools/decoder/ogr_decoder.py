from pathlib import Path

from europa_1400_tools.cli.common_options import CommonOptions
from europa_1400_tools.const import OGR_EXTENSION
from europa_1400_tools.construct.ogr import Ogr
from europa_1400_tools.decoder.base_decoder import BaseDecoder


class OgrDecoder(BaseDecoder[Ogr]):
    """Decoder for OGR files."""

    def __init__(self):
        super().__init__(Ogr)

    @property
    def file_suffix(self) -> str:
        return OGR_EXTENSION

    @property
    def is_archive(self) -> bool:
        return True

    @property
    def is_single_file(self) -> bool:
        return False

    @property
    def game_path(self) -> Path:
        return CommonOptions.instance.game_groups_path

    @property
    def extracted_path(self) -> Path:
        return CommonOptions.instance.extracted_groups_path

    @property
    def decoded_path(self) -> Path:
        return CommonOptions.instance.decoded_groups_path
