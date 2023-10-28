import json
import logging
import pickle
from dataclasses import dataclass, field
from pathlib import Path

from dataclasses_json import config, dataclass_json
from PIL import Image

from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.const import (
    BGF_EXTENSION,
    BMP_EXTENSION,
    JSON_EXTENSION,
    OUTPUT_META_DIR,
    PICKLE_EXTENSION,
    PNG_EXTENSION,
)
from europa1400_tools.construct.bgf import Bgf
from europa1400_tools.construct.txs import Txs
from europa1400_tools.extractor.file_extractor import FileExtractor
from europa1400_tools.helpers import get_files, normalize, rebase_path
from europa1400_tools.models.metadata import (
    AnimationMetadata,
    ObjectMetadata,
    TextureMetadata,
)
from europa1400_tools.rich.progress import Progress


class ObjectsPreprocessor:
    """Preprocess objects."""

    def preprocess_objects(
        self,
        texture_paths: list[Path],
        object_pickle_paths: list[Path],
        txs_pickle_paths: list[Path],
        animation_metadatas: list[AnimationMetadata],
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
                    CommonOptions.instance.decoded_objects_path
                ).with_suffix(BGF_EXTENSION)

                progress.file_path = relative_path.as_posix()
                object_metadata_path = (
                    CommonOptions.instance.converted_objects_path
                    / OUTPUT_META_DIR
                    / relative_path
                ).with_suffix(JSON_EXTENSION)

                if not object_metadata_path.parent.exists():
                    object_metadata_path.parent.mkdir(parents=True)

                if object_metadata_path.exists() and CommonOptions.instance.use_cache:
                    object_metadata = ObjectMetadata.from_json(
                        object_metadata_path.read_text()
                    )
                    object_metadatas.append(object_metadata)

                    for object_texture_metadata in object_metadata.textures:
                        if object_texture_metadata in texture_metadatas:
                            continue

                        texture_metadatas.append(object_texture_metadata)

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

                txs: Txs | None = None

                if txs_pickle_path is not None:
                    relative_txs_path = txs_pickle_path.relative_to(
                        CommonOptions.instance.decoded_txs_path
                    )
                    with open(txs_pickle_path, "rb") as txs_pickle_file:
                        txs = pickle.load(txs_pickle_file)

                object_metadata = ObjectMetadata(
                    name=bgf.name,
                    path=relative_path,
                    textures=[],
                    animations=[],
                    txs_path=relative_txs_path,
                )

                for texture in bgf.textures:
                    texture_metadata: TextureMetadata | None = next(
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

                    if (
                        texture_path is None
                        and txs is not None
                        and len(txs.texture_names) > 0
                    ):
                        texture_path = next(
                            (
                                texture_path
                                for texture_path in texture_paths
                                if normalize(texture_path.stem)
                                == normalize(list(txs.texture_names)[0])
                            ),
                            None,
                        )

                    texture_name = Path(texture.name).stem

                    if texture_path is None:
                        bmp_path = (
                            CommonOptions.instance.extracted_textures_path
                            / Path(texture_name).with_suffix(BMP_EXTENSION)
                        )
                        png_path = (
                            CommonOptions.instance.converted_textures_path
                            / Path(texture_name).with_suffix(PNG_EXTENSION)
                        )
                    else:
                        bmp_path = texture_path
                        png_path = (
                            rebase_path(
                                texture_path,
                                CommonOptions.instance.extracted_textures_path,
                                CommonOptions.instance.converted_textures_path,
                            )
                            .with_stem(texture_name)
                            .with_suffix(PNG_EXTENSION)
                        )

                    relative_png_path = png_path.relative_to(
                        CommonOptions.instance.converted_textures_path
                    )
                    texture_metadata = TextureMetadata(
                        name=texture_name,
                        path=relative_png_path,
                        has_transparency=texture.num0B != 0,
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
                        CommonOptions.instance.converted_textures_path
                    )
                    texture_metadata.path = relative_png_path

                    object_metadata.textures.append(texture_metadata)
                    texture_metadatas.append(texture_metadata)

                for animation_metadata in animation_metadatas:
                    normalized_baf_name = normalize(animation_metadata.name)
                    normalized_object_name = normalize(object_metadata.name)

                    split_baf_name = normalized_baf_name.split("_")
                    split_object_name = normalized_object_name.split("_")

                    has_identical_part: bool = False

                    for baf_name_part in split_baf_name:
                        if baf_name_part in split_object_name:
                            has_identical_part = True
                            break

                    has_identical_vertices_count: bool = (
                        bgf.mapping_object.vertex_mapping_count
                        == animation_metadata.vertices_count
                    )

                    if has_identical_part and has_identical_vertices_count:
                        object_metadata.animations.append(animation_metadata)

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
