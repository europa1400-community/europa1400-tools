from pathlib import Path

from europa_1400_tools.common_options import CommonOptions
from europa_1400_tools.construct.ageb import AGeb
from europa_1400_tools.converter.base_converter import BaseConverter, ConstructType
from europa_1400_tools.decoder.ageb_decoder import AGebDecoder


class AGebConverter(BaseConverter):
    """Convert AGeb files."""

    def __init__(self, common_options: CommonOptions):
        super().__init__(common_options, AGeb, AGebDecoder)

    @property
    def decoded_path(self) -> Path:
        return self.common_options.decoded_ageb_path

    @property
    def converted_path(self) -> Path:
        return self.common_options.converted_ageb_path

    @property
    def is_single_output_file(self) -> bool:
        return True

    def convert(
        self,
        value: ConstructType,
        output_path: Path,
    ) -> list[Path]:
        ageb_json = value.to_json()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(ageb_json, encoding="utf-8")

        return [output_path]
