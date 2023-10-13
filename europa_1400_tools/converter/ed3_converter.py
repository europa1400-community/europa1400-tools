import logging
from pathlib import Path
from timeit import default_timer as timer

from europa_1400_tools.const import JSON_EXTENSION, TargetFormat
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

        time_start = timer()

        ed3 = Ed3.from_file(file_path)

        time_end = timer()
        time_decode = time_end - time_start

        logging.debug(f"Decoded {file_path} in {time_decode:.2f}s")

        time_start = timer()

        ed3_json = ed3.to_json()

        time_end = timer()
        time_encode = time_end - time_start

        logging.debug(f"Encoded {file_path} in {time_encode:.2f}s")

        time_start = timer()

        output_file_path = rebase_path(file_path, base_path, output_path).with_suffix(
            JSON_EXTENSION
        )
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        output_file_path.write_text(ed3_json, encoding="utf-8")

        time_end = timer()
        time_write = time_end - time_start

        logging.debug(f"Wrote {output_file_path} in {time_write:.2f}s")

        return [output_file_path]
