from pathlib import Path

from europa_1400_tools.common_options import CommonOptions
from europa_1400_tools.const import ED3_EXTENSION
from europa_1400_tools.construct.ed3 import Ed3
from europa_1400_tools.decoder.base_decoder import BaseDecoder


class Ed3Decoder(BaseDecoder[Ed3]):
    """Decoder for ED3 files."""

    def __init__(self, common_options: CommonOptions):
        super().__init__(common_options, Ed3)

    @property
    def file_suffix(self) -> str:
        return ED3_EXTENSION

    @property
    def is_archive(self) -> bool:
        return True

    @property
    def is_single_file(self) -> bool:
        return False

    @property
    def game_path(self) -> Path:
        return self.common_options.game_scenes_path

    @property
    def extracted_path(self) -> Path | None:
        return self.common_options.extracted_scenes_path

    @property
    def decoded_path(self) -> Path:
        return self.common_options.decoded_scenes_path
