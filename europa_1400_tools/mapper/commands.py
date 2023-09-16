"""Command line interface for europa_1400_tools."""

import logging
import pickle
from pathlib import Path
from typing import Annotated, Optional

import numpy as np
import typer

from europa_1400_tools.const import (
    MAPPED_ANIMATONS_PICKLE,
    OUTPUT_ANIMATIONS_DIR,
    OUTPUT_OBJECTS_DIR,
    PICKLE_EXTENSION,
)
from europa_1400_tools.construct.baf import Baf
from europa_1400_tools.construct.bgf import Bgf
from europa_1400_tools.decoder.commands import decode_animations, decode_objects
from europa_1400_tools.helpers import get_files
from europa_1400_tools.mapper.animations_mapper import AnimationsMapper
from europa_1400_tools.models import CommonOptions

app = typer.Typer()


@app.command("animations")
def map_animations(
    ctx: typer.Context,
    decoded_animations_path: Annotated[Optional[Path], typer.Option()] = None,
    decoded_objects_path: Annotated[Optional[Path], typer.Option()] = None,
    animation_path: Annotated[Optional[Path], typer.Option()] = None,
    object_path: Annotated[Optional[Path], typer.Option()] = None,
) -> Path:
    """Map animation files to object files."""

    common_options: CommonOptions = ctx.obj
    output_path = common_options.output_path / MAPPED_ANIMATONS_PICKLE

    extracted_animations_path = common_options.extracted_path / Path(
        OUTPUT_ANIMATIONS_DIR
    )
    extracted_objects_path = common_options.extracted_path / Path(OUTPUT_OBJECTS_DIR)

    animations_pickle_paths: list[Path] = []
    objects_pickle_paths: list[Path] = []

    if decoded_animations_path is None:
        animations_pickle_paths = decode_animations(ctx)
    else:
        animations_pickle_paths = get_files(decoded_animations_path, PICKLE_EXTENSION)

    if decoded_objects_path is None:
        objects_pickle_paths = decode_objects(ctx)
    else:
        objects_pickle_paths = get_files(decoded_objects_path, PICKLE_EXTENSION)

    objects_pickle_paths = [
        object_pickle_path for object_pickle_path in objects_pickle_paths
    ]

    bafs: list[Baf] = []
    bgfs: list[Bgf] = []

    for animation_pickle_path in animations_pickle_paths:
        with open(animation_pickle_path, "rb") as animation_pickle_file:
            baf: Baf = pickle.load(animation_pickle_file)
            bafs.append(baf)

    for object_pickle_path in objects_pickle_paths:
        with open(object_pickle_path, "rb") as object_pickle_file:
            bgf: Bgf = pickle.load(object_pickle_file)
            bgfs.append(bgf)

    bgf_to_vertices: dict[Path, np.ndarray] = {}

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

    baf_to_bgfs: dict[Path, list[Path]] = {}

    missing_count = 0
    for baf in bafs:
        mapped_bgfs = AnimationsMapper.map_animation(baf, bgf_to_vertices)

        stripped_baf_path = baf.path.relative_to(extracted_animations_path)

        if len(mapped_bgfs) == 0:
            missing_count += 1
            logging.warning(f"Could not find mapping for {stripped_baf_path}.")

            baf_to_bgfs[stripped_baf_path] = []

            continue

        for bgf in mapped_bgfs:
            stripped_bgf_path = Path(bgf).relative_to(extracted_objects_path)
            baf_to_bgfs[stripped_baf_path] = [stripped_bgf_path]

    logging.info(f"Found mapping for {len(bafs) - missing_count} animations.")

    with open(output_path, "wb") as output_file:
        pickle.dump(baf_to_bgfs, output_file)

    return output_path
