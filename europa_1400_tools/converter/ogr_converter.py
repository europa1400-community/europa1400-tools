import dataclasses
import json
from pathlib import Path

from europa_1400_tools.common_options import (
    OgrDummyElementJson,
    OgrElementJson,
    OgrJson,
    OgrLightBlockJson,
    OgrLightElementJson,
    OgrObjectElementJson,
    OgrTransformJson,
    VertexJson,
)
from europa_1400_tools.const import JSON_EXTENSION, OgrElementType, TargetFormat
from europa_1400_tools.construct.ogr import Ogr
from europa_1400_tools.converter.base_converter import BaseConverter, ConstructType
from europa_1400_tools.decoder.ogr_decoder import OgrDecoder
from europa_1400_tools.helpers import rebase_path


class OgrConverter(BaseConverter):
    """Converter for OGR files."""

    def __init__(self, common_options):
        super().__init__(common_options, Ogr, OgrDecoder)

    @property
    def decoded_path(self) -> Path:
        return self.common_options.decoded_groups_path

    @property
    def converted_path(self) -> Path:
        return self.common_options.converted_groups_path

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
