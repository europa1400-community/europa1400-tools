from pathlib import Path

from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.const import ED3_EXTENSION
from europa1400_tools.construct.ed3 import Ed3
from europa1400_tools.decoder.base_decoder import BaseDecoder


class Ed3Decoder(BaseDecoder[Ed3]):
    """Decoder for ED3 files."""

    def __init__(self):
        super().__init__(Ed3)

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
        return CommonOptions.instance.game_scenes_path

    @property
    def extracted_path(self) -> Path | None:
        return CommonOptions.instance.extracted_scenes_path

    @property
    def decoded_path(self) -> Path:
        return CommonOptions.instance.decoded_scenes_path
