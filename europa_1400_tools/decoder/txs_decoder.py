from pathlib import Path

from europa_1400_tools.common_options import CommonOptions
from europa_1400_tools.const import TXS_EXTENSION
from europa_1400_tools.construct.txs import Txs
from europa_1400_tools.decoder.base_decoder import BaseDecoder


class TxsDecoder(BaseDecoder[Txs]):
    """Decoder for TXS files."""

    def __init__(self, common_options: CommonOptions):
        super().__init__(common_options, Txs)

    @property
    def file_suffix(self) -> str:
        return TXS_EXTENSION

    @property
    def is_archive(self) -> bool:
        return True

    @property
    def is_single_file(self) -> bool:
        return False

    @property
    def game_path(self) -> Path:
        return self.common_options.game_objects_path

    @property
    def extracted_path(self) -> Path | None:
        return self.common_options.extracted_txs_path

    @property
    def decoded_path(self) -> Path:
        return self.common_options.decoded_txs_path
