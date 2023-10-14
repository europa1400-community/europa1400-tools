import logging
import pickle
from pathlib import Path

from PIL import Image

from europa_1400_tools.const import PNG_EXTENSION
from europa_1400_tools.construct.bgf import Bgf
from europa_1400_tools.construct.txs import Txs
from europa_1400_tools.helpers import normalize, rebase_path
from europa_1400_tools.models import CommonOptions


class TexturesPreprocessor:
    @staticmethod
    def preprocess_textures(
        common_options: CommonOptions,
        extracted_texture_paths: list[Path],
        object_pickle_paths: list[Path],
        txs_pickle_paths: list[Path],
    ) -> list[Path]:
        """Preprocess textures."""

        for object_pickle_path in object_pickle_paths:
            with open(object_pickle_path, "rb") as object_pickle_file:
                bgf: Bgf = pickle.load(object_pickle_file)

            txs_pickle_path = next(
                (
                    txs_pickle_path
                    for txs_pickle_path in txs_pickle_paths
                    if txs_pickle_path.stem == bgf.name
                ),
                None,
            )

            txs: Txs | None = None

            if txs_pickle_path is not None:
                with open(txs_pickle_path, "rb") as txs_pickle_file:
                    txs = pickle.load(txs_pickle_file)

            for texture in bgf.textures:
                is_texture_path: bool = texture.name_normalized in [
                    normalize(extracted_texture_path.stem)
                    for extracted_texture_path in extracted_texture_paths
                ]
                has_transparency: bool = texture.num0B != 0
                has_txs: bool = txs is not None and len(txs.texture_names) > 0

                file_name_to_file_path: dict[str, Path] = {}
                file_names: list[str]

                if is_texture_path or not has_txs:
                    file_names = [texture.name]
                else:
                    file_names = txs.texture_names

                file_names_normalized = [
                    normalize(file_name) for file_name in file_names
                ]

                for i, file_name in enumerate(file_names):
                    if file_name in file_name_to_file_path.keys():
                        continue

                    file_name_normalized = file_names_normalized[i]
                    file_path: Path | None = next(
                        (
                            texture_path
                            for j, texture_path in enumerate(extracted_texture_paths)
                            if normalize(extracted_texture_paths[j])
                            == file_name_normalized
                        ),
                        None,
                    )

                    is_dummy_texture: bool = file_path is None

                    if is_dummy_texture:
                        file_path = common_options.extracted_textures_path / Path(
                            file_name
                        )

                    png_file_path = rebase_path(
                        file_path,
                        common_options.extracted_textures_path,
                        common_options.converted_textures_path,
                    ).with_suffix(PNG_EXTENSION)

                    logging.debug(f"Preprocessing {file_path}")

                    if is_dummy_texture:
                        create_dummy_texture(png_file_path)
                    elif has_transparency:
                        convert_bmp_to_png_with_transparency(file_path, png_file_path)
                    else:
                        convert_bmp_to_png(file_path, png_file_path)

                    file_name = png_file_path.name
                    file_path = png_file_path

                    file_name_to_file_path[file_name] = file_path

        return file_name_to_file_path.values()


@staticmethod
def create_dummy_texture(output_path: Path, width: int = 1, height: int = 1) -> None:
    """Create a transparent texture with the specified dimensions."""

    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True)

    texture = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    texture.save(output_path)


@staticmethod
def convert_bmp_to_png_with_transparency(bmp_path: Path, output_path: Path) -> None:
    """Converts a BMP image to a PNG image with zero pixels being transparency."""

    bmp_image = Image.open(bmp_path)
    bmp_image = bmp_image.convert("RGB")
    png_image = Image.new("RGBA", bmp_image.size)

    for x in range(bmp_image.width):
        for y in range(bmp_image.height):
            r, g, b = bmp_image.getpixel((x, y))

            if r == 0 and g == 0 and b == 0:
                png_image.putpixel((x, y), (0, 0, 0, 0))
            else:
                png_image.putpixel((x, y), (r, g, b, 255))

    png_image.save(output_path, format="png")


@staticmethod
def convert_bmp_to_png(bmp_path: Path, output_path: Path) -> None:
    """Converts a BMP image to a PNG image."""

    bmp_image = Image.open(bmp_path)
    bmp_image = bmp_image.convert("RGB")
    png_image = Image.new("RGB", bmp_image.size)
    png_image.save(output_path, format="png")
