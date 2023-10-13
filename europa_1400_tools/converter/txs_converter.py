from pathlib import Path

from europa_1400_tools.const import JSON_EXTENSION, TargetFormat
from europa_1400_tools.construct.txs import Txs
from europa_1400_tools.converter.base_converter import BaseConverter
from europa_1400_tools.helpers import rebase_path


class TxsConverter(BaseConverter):
    """Convert TXS files."""

    def convert_file(
        self,
        file_path: Path,
        output_path: Path,
        base_path: Path,
        target_format: TargetFormat,
        create_subdirectories: bool = False,
    ) -> list[Path]:
        """Convert txs file and export to output_path."""

        txs = Txs.from_file(file_path)
        txs_json = txs.to_json()

        output_path = output_path / rebase_path(
            file_path, base_path, output_path
        ).with_suffix(JSON_EXTENSION)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(txs_json, encoding="utf-8")

        return [output_path]
