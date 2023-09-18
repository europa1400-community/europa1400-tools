import logging
from pathlib import Path

from europa_1400_tools.const import ED3_EXCLUDE, JSON_EXTENSION, TargetFormat
from europa_1400_tools.construct.ed3 import Ed3
from europa_1400_tools.converter.base_converter import BaseConverter
from europa_1400_tools.helpers import rebase_path


class Ed3Converter(BaseConverter):
    """Convert Ed3 files."""

    def convert_file(
        self,
        file_path: Path,
        output_path: Path,
        base_path: Path,
        target_format: TargetFormat,
        create_subdirectories: bool = False,
    ) -> list[Path]:
        """Convert Ed3 file and export to output_path."""

        if file_path.name in ED3_EXCLUDE:
            logging.warning(f"Skipping {file_path}")
            return []

        ed3 = Ed3.from_file(file_path)
        ed3_json = ed3.to_json()

        output_file_path = rebase_path(file_path, base_path, output_path).with_suffix(
            JSON_EXTENSION
        )
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        output_file_path.write_text(ed3_json, encoding="utf-8")

        return [output_file_path]
