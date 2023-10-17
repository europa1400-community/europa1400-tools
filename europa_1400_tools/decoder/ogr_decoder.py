from pathlib import Path

from europa_1400_tools.common_options import CommonOptions
from europa_1400_tools.const import OGR_EXTENSION
from europa_1400_tools.construct.ogr import Ogr
from europa_1400_tools.decoder.base_decoder import BaseDecoder


class OgrDecoder(BaseDecoder[Ogr]):
    """Decoder for OGR files."""

    def __init__(self, common_options: CommonOptions):
        super().__init__(common_options, Ogr)

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
        return self.common_options.game_groups_path

    @property
    def extracted_path(self) -> Path:
        return self.common_options.extracted_groups_path

    @property
    def decoded_path(self) -> Path:
        return self.common_options.decoded_groups_path
