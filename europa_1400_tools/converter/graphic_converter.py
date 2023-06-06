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

        if value.pixel_data:
            pixel_data_rgb = value.pixel_data
            pixel_data_rgba: list[int] = [
                int.from_bytes(pixel_data_rgb[i : i + 3], "little") + 0xFF000000
                for i in range(0, len(pixel_data_rgb), 3)
            ]
            image.putdata(pixel_data_rgba)
            return image

        if value.graphic_rows:
            const_transparent = int.from_bytes(b"\xFF\xFF\xFF\x00", "little")
            image_data: list[int] = []
            for i, graphic_row in enumerate(value.graphic_rows):
                row_data: list[int] = []
                for j, transparency_block in enumerate(graphic_row.transparency_blocks):
                    block_data: list[int] = []
                    for _ in range(transparency_block.size_transparent // 3):
                        block_data += [const_transparent]
                    pixel_data_rgba = [
                        int.from_bytes(
                            transparency_block.pixel_data[i : i + 3], "little"
                        )
                        + 0xFF000000
                        for i in range(0, len(transparency_block.pixel_data), 3)
                    ]
                    block_data.extend(pixel_data_rgba)
                    row_data.extend(block_data)
                image_data.extend(row_data)

            length_check = value.width * value.height
            length_actual = len(image_data)
            assert length_check == length_actual
            image.putdata(image_data)
            return image

        raise ValueError("Graphic has no pixel data or graphic rows")

    @staticmethod
    def convert_and_export(value: Graphic, output_path: Path, **kwargs) -> list[Path]:
        """Convert Graphics and export to output_path."""

        if "name" not in kwargs or "index" not in kwargs:
            raise ValueError("name and index must be provided")

        name = kwargs["name"]
        index = kwargs["index"]

        if not output_path.exists():
            output_path.mkdir(parents=True)

        output_file_path = output_path / Path(f"{name}_{index}").with_suffix(
            PNG_EXTENSION
        )

        image = GraphicConverter.convert(value, **kwargs)
        image.save(output_file_path)

        return [output_file_path]
