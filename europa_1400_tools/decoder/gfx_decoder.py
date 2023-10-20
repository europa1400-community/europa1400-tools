from pathlib import Path

from europa_1400_tools.cli.common_options import CommonOptions
from europa_1400_tools.const import GFX_EXTENSION
from europa_1400_tools.construct.gfx import Gfx
from europa_1400_tools.decoder.base_decoder import BaseDecoder


class GfxDecoder(BaseDecoder[Gfx]):
    """Decoder for Gfx files."""

    def __init__(self):
        super().__init__(Gfx)

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
        return CommonOptions.instance.game_gfx_path

    @property
    def extracted_path(self) -> Path | None:
        return None

    @property
    def decoded_path(self) -> Path:
        return CommonOptions.instance.decoded_gfx_path
