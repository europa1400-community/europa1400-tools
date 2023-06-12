import dataclasses
import json
from pathlib import Path

from europa_1400_tools.const import JSON_EXTENSION, OgrElementType
from europa_1400_tools.construct.ogr import Ogr
from europa_1400_tools.converter.base_converter import BaseConverter
from europa_1400_tools.models import (
    OgrDummyElementJson,
    OgrElementJson,
    OgrJson,
    OgrLightBlockJson,
    OgrLightElementJson,
    OgrObjectElementJson,
    OgrTransformJson,
    VertexJson,
)


class OgrConverter(BaseConverter[Ogr, OgrJson]):
    """Converter for OGR files."""

    @staticmethod
    def convert(value: Ogr, **kwargs) -> OgrJson:
        """Convert value to another format."""

        ogr_elements_json: list[OgrElementJson] = []

        for group_element in value.group_elements:
            ogr_element_json: OgrElementJson

            if group_element.type == 2:
                if not group_element.dummy_element:
                    raise ValueError("Dummy element is None.")

                position = VertexJson(
                    x=group_element.dummy_element.object_data.offset.x,
                    y=group_element.dummy_element.object_data.offset.y,
                    z=group_element.dummy_element.object_data.offset.z,
                )
                rotation = VertexJson(
                    x=group_element.dummy_element.object_data.data.x,
                    y=group_element.dummy_element.object_data.data.y,
                    z=group_element.dummy_element.object_data.data.z,
                )
                transform = OgrTransformJson(
                    position=position,
                    rotation=rotation,
                )

                ogr_element_json = OgrDummyElementJson(
                    name=group_element.name,
                    type=OgrElementType.DUMMY.value,
                    transform=transform,
                )
            elif group_element.type == 4:
                if not group_element.object_element:
                    raise ValueError("Object element is None.")

                position = VertexJson(
                    x=group_element.object_element.object_data.offset.x,
                    y=group_element.object_element.object_data.offset.y,
                    z=group_element.object_element.object_data.offset.z,
                )
                rotation = VertexJson(
                    x=group_element.object_element.object_data.data.x,
                    y=group_element.object_element.object_data.data.y,
                    z=group_element.object_element.object_data.data.z,
                )
                transform = OgrTransformJson(
                    position=position,
                    rotation=rotation,
                )

                additional_transform: OgrTransformJson | None = None

                if group_element.object_element.object_data_additional:
                    additional_position = VertexJson(
                        x=group_element.object_element.object_data_additional.offset.x,
                        y=group_element.object_element.object_data_additional.offset.y,
                        z=group_element.object_element.object_data_additional.offset.z,
                    )
                    additional_rotation = VertexJson(
                        x=group_element.object_element.object_data_additional.data.x,
                        y=group_element.object_element.object_data_additional.data.y,
                        z=group_element.object_element.object_data_additional.data.z,
                    )
                    additional_transform = OgrTransformJson(
                        position=additional_position,
                        rotation=additional_rotation,
                    )

                ogr_element_json = OgrObjectElementJson(
                    name=group_element.name,
                    type=OgrElementType.OBJECT.value,
                    transform=transform,
                    object_name=group_element.object_element.name,
                    additional_transform=additional_transform,
                )
            elif (
                group_element.type == 5
                or group_element.type == 6
                or group_element.type == 7
                or group_element.type == 8
            ):
                if not group_element.light_element:
                    raise ValueError("Light element is None.")

                ogr_light_blocks_json: list[OgrLightBlockJson] = []

                for light_data_block in group_element.light_element.light_data_blocks:
                    ogr_light_block_json = OgrLightBlockJson(
                        values=light_data_block.data,
                    )
                    ogr_light_blocks_json.append(ogr_light_block_json)

                ogr_element_json = OgrLightElementJson(
                    name=group_element.name,
                    type=OgrElementType.LIGHT.value,
                    blocks=ogr_light_blocks_json,
                )
            else:
                raise ValueError(f"Unknown OGR element type: {group_element.type}.")

            ogr_elements_json.append(ogr_element_json)

        name: str = kwargs.get("name", ogr_elements_json[0].name)
        ogr_json = OgrJson(name, ogr_elements_json)

        return ogr_json

    @staticmethod
    def convert_and_export(value: Ogr, output_path: Path, **kwargs) -> list[Path]:
        """Convert value and export to output_path."""

        if not output_path.exists():
            output_path.mkdir(parents=True)

        if not output_path.is_dir():
            raise ValueError("Output path is not a directory.")

        name = kwargs.get("name")

        if not name:
            raise ValueError("Name is not set.")

        ogr_json = OgrConverter.convert(value, **kwargs)
        ogr_dict = dataclasses.asdict(ogr_json)
        ogr_json_text = json.dumps(ogr_dict, indent=4)

        json_output_path = output_path / Path(name).with_suffix(JSON_EXTENSION)
        json_output_path.write_text(ogr_json_text, encoding="utf-8")

        return [json_output_path]
