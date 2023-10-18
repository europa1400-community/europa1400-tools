"""Command line interface for europa_1400_tools."""

import logging
import pickle
from pathlib import Path

import numpy as np
import typer

from europa_1400_tools.common_options import CommonOptions
from europa_1400_tools.const import (
    MAPPED_ANIMATONS_PICKLE,
    OUTPUT_ANIMATIONS_DIR,
    OUTPUT_OBJECTS_DIR,
    PICKLE_EXTENSION,
)
from europa_1400_tools.construct.baf import Baf
from europa_1400_tools.construct.bgf import Bgf
from europa_1400_tools.decoder.commands import (
    cmd_decode_animations,
    cmd_decode_objects,
    cmd_decode_txs,
)
from europa_1400_tools.helpers import get_files
from europa_1400_tools.preprocessor.animations_preprocessor import (
    AnimationsPreprocessor,
)
from europa_1400_tools.preprocessor.objects_preprocessor import ObjectsPreprocessor

app = typer.Typer()


@app.command("textures")
def cmd_preprocess_textures(
    ctx: typer.Context,
) -> list[Path]:
    common_options: CommonOptions = ctx.obj

    converted_texture_paths = ObjectsPreprocessor.preprocess_objects(common_options)
    return converted_texture_paths


@app.command("animations")
def cmd_preprocess_animations(
    ctx: typer.Context,
) -> Path:
    """Command to map animation files to object files."""

    common_options: CommonOptions = ctx.obj

    output_path = common_options.output_path / MAPPED_ANIMATONS_PICKLE

    extracted_animations_path = common_options.extracted_path / Path(
        OUTPUT_ANIMATIONS_DIR
    )
    extracted_objects_path = common_options.extracted_path / Path(OUTPUT_OBJECTS_DIR)

    animations_pickle_paths: list[Path] = []
    objects_pickle_paths: list[Path] = []

    if common_options.decoded_animations_path.exists() and common_options.use_cache:
        animations_pickle_paths = get_files(
            common_options.decoded_animations_path, PICKLE_EXTENSION
        )
    else:
        animations_pickle_paths = cmd_decode_animations(ctx)

    if common_options.decoded_objects_path.exists() and common_options.use_cache:
        objects_pickle_paths = get_files(
            common_options.decoded_objects_path, PICKLE_EXTENSION
        )
    else:
        objects_pickle_paths = cmd_decode_objects(ctx)

    baf_to_bgfs, missing_paths = preprocess_animations(
        extracted_objects_path,
        extracted_animations_path,
        objects_pickle_paths,
        animations_pickle_paths,
    )

    with open(output_path, "wb") as output_file:
        pickle.dump(baf_to_bgfs, output_file)

    # output the missing paths into self.common_options.missing_paths_path text file

    with open(common_options.missing_paths_path, "w") as missing_paths_file:
        for missing_path in missing_paths:
            missing_paths_file.write(f"{missing_path}\n")

    return output_path


def preprocess_animations(
    extracted_objects_path: Path,
    extracted_animations_path: Path,
    decoded_objects_paths: list[Path],
    decoded_animations_paths: list[Path],
) -> tuple[dict[Path, list[Path]], list[Path]]:
    """Map animation files to object files."""

    bafs: list[Baf] = []
    bgfs: list[Bgf] = []

    logging.info("Loading animations and objects.")

    for animation_pickle_path in decoded_animations_paths:
        with open(animation_pickle_path, "rb") as animation_pickle_file:
            baf: Baf = pickle.load(animation_pickle_file)
            bafs.append(baf)

    for object_pickle_path in decoded_objects_paths:
        with open(object_pickle_path, "rb") as object_pickle_file:
            bgf: Bgf = pickle.load(object_pickle_file)
            bgfs.append(bgf)

    bgf_to_vertices: dict[Path, np.ndarray] = {}

    logging.info("Extracting vertices for objects.")

    for bgf in bgfs:
        bgf_to_vertices[bgf.path] = np.array(
            [
                [
                    vertex_mapping.vertex1.x,
                    vertex_mapping.vertex1.y,
                    vertex_mapping.vertex1.z,
                ]
                for vertex_mapping in bgf.mapping_object.vertex_mappings
            ],
            dtype=np.float32,
        )

    baf_path_to_bgf_paths: dict[Path, list[Path]] = {}

    missing_count = 0
    missing_paths: list[Path] = []
    for baf in bafs:
        logging.debug(f"Mapping {baf.path}.")
        mapped_bgf_paths = AnimationsPreprocessor.map_animation(baf, bgf_to_vertices)

        stripped_baf_path = baf.path.relative_to(extracted_animations_path)

        if len(mapped_bgf_paths) == 0:
            missing_count += 1
            logging.warning(f"Could not find mapping for {stripped_baf_path}.")
            missing_paths.append(stripped_baf_path)

            baf_path_to_bgf_paths[stripped_baf_path] = []

            continue

        baf_path_to_bgf_paths[stripped_baf_path] = []

        for bgf_path in mapped_bgf_paths:
            stripped_bgf_path = bgf_path.relative_to(extracted_objects_path)
            baf_path_to_bgf_paths[stripped_baf_path].append(stripped_bgf_path)

    logging.info(f"Found mapping for {len(bafs) - missing_count} animations.")

    return baf_path_to_bgf_paths, missing_paths
