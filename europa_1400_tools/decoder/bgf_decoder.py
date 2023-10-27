from pathlib import Path

from europa_1400_tools.cli.common_options import CommonOptions
from europa_1400_tools.const import BGF_EXTENSION
from europa_1400_tools.construct.bgf import Bgf
from europa_1400_tools.decoder.base_decoder import BaseDecoder


class BgfDecoder(BaseDecoder[Bgf]):
    """Decoder for BGF files."""

    def __init__(self):
        super().__init__(Bgf)

    @property
    def file_suffix(self) -> str:
        return BGF_EXTENSION

    @property
    def is_archive(self) -> bool:
        return True

    @property
    def is_single_file(self) -> bool:
        return False

    @property
    def game_path(self) -> Path:
        return CommonOptions.instance.game_objects_path

    @property
    def extracted_path(self) -> Path | None:
        return CommonOptions.instance.extracted_objects_path

    @property
    def decoded_path(self) -> Path:
        return CommonOptions.instance.decoded_objects_path
