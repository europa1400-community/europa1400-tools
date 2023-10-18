import json
import logging
import pickle
from dataclasses import dataclass, field
from pathlib import Path

from dataclasses_json import config, dataclass_json
from PIL import Image

from europa_1400_tools.common_options import CommonOptions
from europa_1400_tools.const import (
    BMP_EXTENSION,
    JSON_EXTENSION,
    PICKLE_EXTENSION,
    PNG_EXTENSION,
)
from europa_1400_tools.construct.bgf import Bgf
from europa_1400_tools.construct.txs import Txs
from europa_1400_tools.extractor.file_extractor import FileExtractor
from europa_1400_tools.helpers import get_files, normalize, rebase_path
from europa_1400_tools.rich.progress import Progress


@dataclass_json
@dataclass
class TextureMetadata:
    """Metadata for a texture."""

    name: str
    path: Path = field(
        metadata=config(
            encoder=lambda path: str(path),
            decoder=lambda path: Path(path),
        )
    )
    has_transparency: bool


@dataclass_json
@dataclass
class ObjectMetadata:
    name: str
    textures: list[TextureMetadata]
    txs_path: Path | None = field(
        metadata=config(
            encoder=lambda path: str(path) if path is not None else None,
            decoder=lambda path: Path(path) if path is not None else None,
        )
    )


class ObjectsPreprocessor:
    """Preprocess objects."""

    common_options: CommonOptions

    def __init__(self, common_options: CommonOptions):
        self.common_options = common_options

    def preprocess_objects(
        self,
        texture_paths: list[Path],
        object_pickle_paths: list[Path],
        txs_pickle_paths: list[Path],
    ) -> list[ObjectMetadata]:
        """Preprocess objects."""

        progress = Progress(
            title="Preprocessing objects",
            total_file_count=len(object_pickle_paths),
        )

        object_metadatas: list[ObjectMetadata] = []
        texture_metadatas: list[TextureMetadata] = []

        with progress:
            for object_pickle_path in object_pickle_paths:
                relative_path = object_pickle_path.relative_to(
                    self.common_options.decoded_objects_path
                )

                progress.file_path = relative_path
                object_metadata_path = (
                    self.common_options.converted_objects_path / relative_path
                ).with_suffix(JSON_EXTENSION)

                if not object_metadata_path.parent.exists():
                    object_metadata_path.parent.mkdir(parents=True)

                if object_metadata_path.exists():
                    object_metadata = ObjectMetadata.from_json(
                        object_metadata_path.read_text()
                    )
                    object_metadatas.append(object_metadata)

                    for texture_metadata in object_metadata.textures:
                        if texture_metadata in texture_metadatas:
                            continue

                        texture_metadatas.append(texture_metadata)

                    progress.cached_file_count += 1
                    continue

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
                relative_txs_path: Path | None = None

                if txs_pickle_path is not None:
                    relative_txs_path = txs_pickle_path.relative_to(
                        self.common_options.decoded_txs_path
                    )
                    with open(txs_pickle_path, "rb") as txs_pickle_file:
                        txs = pickle.load(txs_pickle_file)

                txs: Txs | None = None

                txs_main_texture_name = None

                if txs is not None and len(txs.texture_names) > 0:
                    txs_main_texture_name = list(txs.texture_names)[0]

                object_metadata = ObjectMetadata(
                    name=bgf.name,
                    textures=[],
                    txs_path=relative_txs_path,
                )

                for texture in bgf.textures:
                    texture_metadata = next(
                        (
                            texture_metadata
                            for texture_metadata in texture_metadatas
                            if texture_metadata.name == texture.name
                        ),
                        None,
                    )

                    if texture_metadata is not None:
                        object_metadata.textures.append(texture_metadata)
                        continue

                    texture_path = next(
                        (
                            texture_path
                            for texture_path in texture_paths
                            if normalize(texture_path.stem) == normalize(texture.name)
                        ),
                        None,
                    )

                    if texture_path is None and txs is not None:
                        texture_path = next(
                            (
                                texture_path
                                for texture_path in texture_paths
                                if normalize(texture_path.stem)
                                == normalize(txs_main_texture_name)
                            ),
                            None,
                        )

                    texture_metadata = TextureMetadata(
                        name=Path(texture.name).stem,
                        path=texture_path,
                        has_transparency=texture.num0B != 0,
                    )

                    if texture_metadata.path is None:
                        bmp_path = self.common_options.extracted_textures_path / Path(
                            texture_metadata.name
                        ).with_suffix(BMP_EXTENSION)
                        png_path = self.common_options.converted_textures_path / Path(
                            texture_metadata.name
                        ).with_suffix(PNG_EXTENSION)
                    else:
                        bmp_path = texture_metadata.path
                        png_path = (
                            rebase_path(
                                texture_path,
                                self.common_options.extracted_textures_path,
                                self.common_options.converted_textures_path,
                            )
                            .with_stem(texture_metadata.name)
                            .with_suffix(PNG_EXTENSION)
                        )

                    if not png_path.parent.exists():
                        png_path.parent.mkdir(parents=True)

                    if texture_metadata.has_transparency:
                        pass

                    if texture_metadata.path is None:
                        self.create_dummy_texture(png_path)
                    elif texture_metadata.has_transparency:
                        self.convert_bmp_to_png_with_transparency(bmp_path, png_path)
                    else:
                        self.convert_bmp_to_png(bmp_path, png_path)

                    relative_png_path = png_path.relative_to(
                        self.common_options.converted_textures_path
                    )
                    texture_metadata.path = relative_png_path

                    object_metadata.textures.append(texture_metadata)
                    texture_metadatas.append(texture_metadata)

                object_metadatas.append(object_metadata)
                object_metadata_path.write_text(object_metadata.to_json(indent=4))

                progress.completed_file_count += 1

        return object_metadatas

    @staticmethod
    def create_dummy_texture(
        output_path: Path, width: int = 1, height: int = 1
    ) -> None:
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
        png_image = Image.new("RGBA", bmp_image.size)

        for x in range(bmp_image.width):
            for y in range(bmp_image.height):
                r, g, b = bmp_image.getpixel((x, y))
                png_image.putpixel((x, y), (r, g, b, 255))

        png_image.save(output_path, format="png")
