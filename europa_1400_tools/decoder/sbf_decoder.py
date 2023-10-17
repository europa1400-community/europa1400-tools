from pathlib import Path

from europa_1400_tools.common_options import CommonOptions
from europa_1400_tools.const import SBF_EXTENSION
from europa_1400_tools.construct.sbf import Sbf
from europa_1400_tools.decoder.base_decoder import BaseDecoder


class SbfDecoder(BaseDecoder[Sbf]):
    """Decoder for SBF files."""

    def __init__(self, common_options: CommonOptions):
        super().__init__(common_options, Sbf)

    @property
    def file_suffix(self) -> str:
        return SBF_EXTENSION

    @property
    def is_archive(self) -> bool:
        return False

    @property
    def is_single_file(self) -> bool:
        return False

    @property
    def game_path(self) -> Path:
        return self.common_options.game_sfx_path

    @property
    def extracted_path(self) -> Path | None:
        return None

    @property
    def decoded_path(self) -> Path:
        return self.common_options.decoded_sfx_path
