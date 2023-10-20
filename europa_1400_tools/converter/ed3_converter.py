from pathlib import Path

from europa_1400_tools.cli.convert_options import ConvertOptions
from europa_1400_tools.const import JSON_EXTENSION, TargetFormat
from europa_1400_tools.construct.ed3 import Ed3
from europa_1400_tools.converter.base_converter import BaseConverter, ConstructType
from europa_1400_tools.decoder.ed3_decoder import Ed3Decoder


class Ed3Converter(BaseConverter):
    """Convert Ed3 files."""

    def __init__(self):
        super().__init__(Ed3, Ed3Decoder)

    @property
    def decoded_path(self) -> Path:
        return ConvertOptions.instance.decoded_scenes_path

    @property
    def converted_path(self) -> Path:
        return ConvertOptions.instance.converted_scenes_path

    @property
    def is_single_output_file(self) -> bool:
        return True

    def convert(
        self,
        value: ConstructType,
        output_path: Path,
    ) -> list[Path]:
        value_json = value.to_json()

        json_output_path = (output_path / value.path.name).with_suffix(JSON_EXTENSION)
        json_output_path.parent.mkdir(parents=True, exist_ok=True)
        json_output_path.write_text(value_json, encoding="utf-8")

        return [json_output_path]
