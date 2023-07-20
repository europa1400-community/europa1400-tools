from pathlib import Path

from europa_1400_tools.const import TargetFormat
from europa_1400_tools.construct.aobj import AObj
from europa_1400_tools.converter.base_converter import BaseConverter


class AObjConverter(BaseConverter):
    """Convert AObj files."""

    def convert_file(
        self,
        file_path: Path,
        output_path: Path,
        base_path: Path,
        target_format: TargetFormat,
        create_subdirectories: bool = False,
    ) -> list[Path]:
        """Convert aobj file and export to output_path."""

        aobj = AObj.from_file(file_path)
        aobj_json = aobj.to_json()

        output_path = output_path / Path("object_data.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(aobj_json, encoding="utf-8")

        return [output_path]
