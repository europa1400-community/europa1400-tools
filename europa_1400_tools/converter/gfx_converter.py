from pathlib import Path

from PIL import Image

from europa_1400_tools.const import PNG_EXTENSION, TargetFormat
from europa_1400_tools.construct.gfx import Gfx, Graphic, ShapebankDefinition
from europa_1400_tools.converter.base_converter import BaseConverter


class GfxConverter(BaseConverter):
    """Class for converting the GFX file."""

    def convert_file(
        self,
        file_path: Path,
        output_path: Path,
        base_path: Path,
        target_format: TargetFormat,
        create_subdirectories: bool = False,
    ) -> list[Path]:
        """Convert Gfx graphics to images."""

        gfx = Gfx.from_file(file_path)
        output_file_paths: list[Path] = []
        shapebank_images: dict[str, dict[str, Image.Image]] = {}

        for shapebank_definition in gfx.shapebank_definitions:
            if not shapebank_definition.shapebank:
                continue
            images = self.convert_shapebank(shapebank_definition)
            shapebank_images[shapebank_definition.name] = images

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

    def convert_graphic(
        self,
        graphic: Graphic,
    ) -> Image.Image:
        image = Image.new("RGBA", (graphic.width, graphic.height))

        if graphic.pixel_data:
            pixel_data_rgb = graphic.pixel_data
            pixel_data_rgba: list[int] = [
                int.from_bytes(pixel_data_rgb[i : i + 3], "little") + 0xFF000000
                for i in range(0, len(pixel_data_rgb), 3)
            ]
            image.putdata(pixel_data_rgba)
            return image

        if graphic.graphic_rows:
            const_transparent = int.from_bytes(b"\xFF\xFF\xFF\x00", "little")
            image_data: list[int] = []
            for i, graphic_row in enumerate(graphic.graphic_rows):
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

            length_check = graphic.width * graphic.height
            length_actual = len(image_data)
            assert length_check == length_actual
            image.putdata(image_data)
            return image

        raise ValueError("Graphic has no pixel data or graphic rows")

    def convert_shapebank(
        self,
        shapebank_definition: ShapebankDefinition,
    ) -> dict[str, Image.Image]:
        """Convert Shapebank graphics to images."""

        if not shapebank_definition.shapebank:
            raise ValueError("Shapebank not found.")

        images: dict[str, Image.Image] = {}

        for i, graphic in enumerate(shapebank_definition.shapebank.graphics):
            graphic_name = f"{shapebank_definition.name}_{i}"
            images[graphic_name] = self.convert_graphic(graphic)

        return images
