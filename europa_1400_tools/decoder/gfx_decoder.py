from pathlib import Path

from europa_1400_tools.common_options import CommonOptions
from europa_1400_tools.const import GFX_EXTENSION
from europa_1400_tools.construct.gfx import Gfx
from europa_1400_tools.decoder.base_decoder import BaseDecoder


class GfxDecoder(BaseDecoder[Gfx]):
    """Decoder for Gfx files."""

    def __init__(self, common_options: CommonOptions):
        super().__init__(common_options, Gfx)

    @property
    def file_suffix(self) -> str:
        return GFX_EXTENSION

    @property
    def is_archive(self) -> bool:
        return False

    @property
    def is_single_file(self) -> bool:
        return True

    @property
    def game_path(self) -> Path:
        return self.common_options.game_gfx_path

    @property
    def extracted_path(self) -> Path | None:
        return None

    @property
    def decoded_path(self) -> Path:
        return self.common_options.decoded_gfx_path
