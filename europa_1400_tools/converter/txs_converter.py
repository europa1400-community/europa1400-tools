from pathlib import Path

from europa_1400_tools.cli.common_options import CommonOptions
from europa_1400_tools.cli.convert_options import ConvertOptions
from europa_1400_tools.const import JSON_EXTENSION, TargetFormat
from europa_1400_tools.construct.txs import Txs
from europa_1400_tools.converter.base_converter import BaseConverter, ConstructType
from europa_1400_tools.decoder.txs_decoder import TxsDecoder
from europa_1400_tools.helpers import rebase_path


class TxsConverter(BaseConverter):
    """Convert TXS files."""

    def __init__(self):
        super().__init__(Txs, TxsDecoder)

    @property
    def decoded_path(self) -> Path:
        return ConvertOptions.instance.decoded_txs_path

    @property
    def converted_path(self) -> Path:
        return ConvertOptions.instance.converted_txs_path

    @property
    def is_single_output_file(self) -> bool:
        return False

    def convert(
        self,
        value: ConstructType,
        output_path: Path,
    ) -> list[Path]:
        txs_json = value.to_json()

        output_path = (output_path / value.path.name).with_suffix(JSON_EXTENSION)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(txs_json, encoding="utf-8")

        return [output_path]
