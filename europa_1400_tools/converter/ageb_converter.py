from pathlib import Path

from europa_1400_tools.const import TargetFormat
from europa_1400_tools.construct.ageb import AGeb
from europa_1400_tools.converter.base_converter import BaseConverter


class AGebConverter(BaseConverter):
    """Convert AGeb files."""

    def convert_file(
        self,
        file_path: Path,
        output_path: Path,
        base_path: Path,
        target_format: TargetFormat,
        create_subdirectories: bool = False,
    ) -> list[Path]:
        """Convert AGeb file and export to output_path."""

        ageb = AGeb.from_file(file_path)
        ageb_json = ageb.to_json()

        output_path = output_path / Path("building_data.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(ageb_json, encoding="utf-8")

        return [output_path]
