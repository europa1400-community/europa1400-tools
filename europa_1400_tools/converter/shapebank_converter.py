from pathlib import Path

from PIL import Image

from europa_1400_tools.const import PNG_EXTENSION
from europa_1400_tools.construct.gfx import ShapebankDefinition
from europa_1400_tools.converter.base_converter import BaseConverter
from europa_1400_tools.converter.graphic_converter import GraphicConverter


class ShapebankConverter(BaseConverter[ShapebankDefinition, dict[str, Image.Image]]):
    @staticmethod
    def convert(value: ShapebankDefinition, **kwargs) -> dict[str, Image.Image]:
        """Convert Shapebank graphics to images."""

        if not value.shapebank:
            raise ValueError("Shapebank not found.")

        images: dict[str, Image.Image] = {}

        for i, graphic in enumerate(value.shapebank.graphics):
            graphic_name = f"{value.name}_{i}"
            images[graphic_name] = GraphicConverter.convert(graphic)

        return images

    @staticmethod
    def convert_and_export(
        value: ShapebankDefinition, output_path: Path, **kwargs
    ) -> list[Path]:
        """Convert Shapebank graphics to images."""

        if not output_path.exists():
            output_path.mkdir(parents=True)

        output_file_paths = []

        images = ShapebankConverter.convert(value, **kwargs)

        for name, image in images.items():
            output_file_path = output_path / Path(name).with_suffix(PNG_EXTENSION)
            image.save(output_file_path)
            output_file_paths.append(output_file_path)

        return output_file_paths
