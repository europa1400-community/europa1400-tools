from pathlib import Path

from PIL import Image

from europa_1400_tools.const import PNG_EXTENSION
from europa_1400_tools.construct.gfx import Gfx
from europa_1400_tools.converter.base_converter import BaseConverter
from europa_1400_tools.converter.shapebank_converter import ShapebankConverter


class GfxConverter(BaseConverter[Gfx, dict[str, dict[str, Image.Image]]]):
    """Class for converting the GFX file."""

    @staticmethod
    def convert(value: Gfx, **kwargs) -> dict[str, dict[str, Image.Image]]:
        """Convert Gfx graphics to images."""

        shapebank_images: dict[str, dict[str, Image.Image]] = {}

        for shapebank_definition in value.shapebank_definitions:
            if not shapebank_definition.shapebank:
                continue
            images = ShapebankConverter.convert(shapebank_definition)
            shapebank_images[shapebank_definition.name] = images

        return shapebank_images

    @staticmethod
    def convert_and_export(value: Gfx, output_path: Path, **kwargs) -> list[Path]:
        """Convert Gfx graphics to images."""

        if not output_path.exists():
            output_path.mkdir(parents=True)

        output_file_paths = []

        shapebank_images = GfxConverter.convert(value, **kwargs)

        for name, images in shapebank_images.items():
            shapebank_output_path = output_path / name

            if not shapebank_output_path.exists():
                shapebank_output_path.mkdir(parents=True)

            for image_name, image in images.items():
                output_file_path = shapebank_output_path / Path(image_name).with_suffix(
                    PNG_EXTENSION
                )
                image.save(output_file_path)
                output_file_paths.append(output_file_path)

        return output_file_paths
