from pathlib import Path

from europa_1400_tools.common_options import CommonOptions
from europa_1400_tools.const import DAT_EXTENSION
from europa_1400_tools.construct.ageb import AGeb
from europa_1400_tools.decoder.base_decoder import BaseDecoder


class AGebDecoder(BaseDecoder[AGeb]):
    """Decoder for AGeb files."""

    def __init__(self, common_options: CommonOptions):
        super().__init__(common_options, AGeb)

    @property
    def file_suffix(self) -> str:
        return DAT_EXTENSION

    @property
    def is_archive(self) -> bool:
        return False

    @property
    def is_single_file(self) -> bool:
        return True

    @property
    def game_path(self) -> Path:
        return self.common_options.game_ageb_path

    @property
    def extracted_path(self) -> Path | None:
        return None

    @property
    def decoded_path(self) -> Path:
        return self.common_options.decoded_ageb_path
