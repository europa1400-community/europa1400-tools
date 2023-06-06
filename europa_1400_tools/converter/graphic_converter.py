from pathlib import Path

from PIL import Image

from europa_1400_tools.const import PNG_EXTENSION
from europa_1400_tools.construct.gfx import Graphic
from europa_1400_tools.converter.base_converter import BaseConverter


class GraphicConverter(BaseConverter[Graphic, Image.Image]):
    """Class for converting GFX graphics."""

    @staticmethod
    def convert(value: Graphic, **kwargs) -> Image.Image:
        """Convert Graphic to Image"""

        image = Image.new("RGBA", (value.width, value.height))

        for i, pixel in enumerate(value.pixels):
            x = i % value.width
            y = i // value.width
            image.putpixel((x, y), (pixel.red, pixel.green, pixel.blue, pixel.alpha))

        return image

        # if value.pixels_rgb:
        #     for i, pixel in enumerate(value.pixels_rgb):
        #         x = i % value.width
        #         y = i // value.width
        #         image.putpixel((x, y), (pixel.red, pixel.green, pixel.blue, 255))

        #     return image

        # if value.graphic_rows:
        #     for i, graphic_row in enumerate(value.graphic_rows):
        #         for transparency_block in graphic_row.transparency_blocks:
        #             for pixel in transparency_block.transparent_pixels_rgba:
        #                 x = i % value.width
        #                 y = i // value.width
        #                 image.putpixel((x, y), (255, 255, 255, 0))
        #             for pixel in transparency_block.color_pixels_rgb:
        #                 x = i % value.width
        #                 y = i // value.width
        #                 image.putpixel(
        #                     (x, y),
        #                     (pixel.red, pixel.green, pixel.blue, 255),
        #                 )

        #     return image

        # raise ValueError("Invalid Graphic")

    @staticmethod
    def convert_and_export(value: Graphic, output_path: Path, **kwargs) -> list[Path]:
        """Convert Graphics and export to output_path."""

        if not output_path.exists():
            output_path.mkdir(parents=True)

        output_file_path = output_path / Path(value.name).with_suffix(PNG_EXTENSION)

        image = GraphicConverter.convert(value, **kwargs)
        image.save(output_file_path)

        return [output_file_path]
