from pathlib import Path

from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.cli.convert_options import ConvertOptions
from europa1400_tools.construct.aobj import AObj
from europa1400_tools.construct.base_construct import BaseConstruct
from europa1400_tools.converter.base_converter import BaseConverter


class AObjConverter(BaseConverter):
    """Convert AObj files."""

    @property
    def decoded_path(self) -> Path:
        return ConvertOptions.instance.decoded_aobj_path

    @property
    def converted_path(self) -> Path:
        return ConvertOptions.instance.converted_aobj_path

    @property
    def is_single_output_file(self) -> bool:
        return True

    def convert(
        self,
        value: AObj,
        output_path: Path,
    ) -> list[Path]:
        """Convert aobj file and export to output_path."""

        aobj_json = value.to_json()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(aobj_json, encoding="utf-8")

        return [output_path]
