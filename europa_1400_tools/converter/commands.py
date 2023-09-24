"""Commands for converting files"""

import logging
from pathlib import Path
from typing import Annotated, List, Optional

import typer

from europa_1400_tools.const import (
    BIN_EXTENSION,
    CONVERTIBLE_PATHS,
    IGNORED_EXTENSIONS,
    SourceFormat,
    TargetFormat,
)
from europa_1400_tools.converter.ageb_converter import AGebConverter
from europa_1400_tools.converter.aobj_converter import AObjConverter
from europa_1400_tools.converter.base_converter import BaseConverter
from europa_1400_tools.converter.bgf_gltf_converter import BgfGltfConverter
from europa_1400_tools.converter.bgf_wavefront_converter import BgfWavefrontConverter
from europa_1400_tools.converter.ed3_converter import Ed3Converter
from europa_1400_tools.converter.gfx_converter import GfxConverter
from europa_1400_tools.converter.ogr_converter import OgrConverter
from europa_1400_tools.converter.sbf_converter import SbfConverter
from europa_1400_tools.extractor.commands import extract_file
from europa_1400_tools.helpers import get_files
from europa_1400_tools.models import CommonOptions

app = typer.Typer()


@app.callback(invoke_without_command=True)
def convert(
    ctx: typer.Context,
    typer_target_format: Optional[TargetFormat.convert_typer()] = typer.Option(
        None, "--target-format", "-t"
    ),
    create_subdirectories: bool = typer.Option(False, "--create-subdirectories", "-c"),
    paths: Annotated[
        Optional[List[Path]], typer.Argument(help="Paths to files or directories.")
    ] = None,
) -> list[Path]:
    """Convert files"""

    common_options: CommonOptions = ctx.obj

    base_path_to_file_paths: dict[Path, list[Path]] = {}

    if not paths:
        paths = [common_options.game_path / path for path in CONVERTIBLE_PATHS]

    for path in paths:
        if path.is_dir():
            if path not in base_path_to_file_paths.keys():
                base_path_to_file_paths[path] = []

            base_path_to_file_paths[path].extend(get_files(path))
        elif path.suffix == BIN_EXTENSION:
            extracted_path = common_options.extracted_path / path.stem

            if extracted_path not in base_path_to_file_paths.keys():
                base_path_to_file_paths[extracted_path] = []

            base_path_to_file_paths[extracted_path].extend(
                extract_file(path, extracted_path)
            )
        else:
            if path not in base_path_to_file_paths.keys():
                base_path_to_file_paths[path.parent] = []

            base_path_to_file_paths[path.parent].append(path)

    format_to_file_paths: dict[SourceFormat, dict[Path, list[Path]]] = {}

    for base_path, file_paths in base_path_to_file_paths.items():
        for file_path in file_paths:
            if file_path.suffix.lower() in IGNORED_EXTENSIONS:
                continue

            source_format = SourceFormat.from_path(file_path)

            if source_format is None:
                suffix: str | None = (
                    file_path.suffix.lower() if file_path.suffix else None
                )
                message: str = (
                    f"Unknown file extension: {suffix}"
                    if suffix
                    else "Unknown file extension"
                )
                logging.warning(f"{message}: {file_path}")
                logging.warning(f"Skipping {file_path}")
                continue

            if source_format not in format_to_file_paths:
                format_to_file_paths[source_format] = {}

            if base_path not in format_to_file_paths[source_format]:
                format_to_file_paths[source_format][base_path] = []

            format_to_file_paths[source_format][base_path].append(file_path)

    output_paths: list[Path] = []
    for source_format, _base_path_to_file_paths in format_to_file_paths.items():
        for base_path, file_paths in _base_path_to_file_paths.items():
            if typer_target_format is None:
                target_format = source_format.target_formats[0]
            else:
                target_format = TargetFormat.from_typer(typer_target_format.value)

            if target_format not in source_format.target_formats:
                logging.warning(
                    f"Cannot convert {source_format} files to {target_format}"
                )
                continue

            converter: BaseConverter

            if source_format == SourceFormat.AOBJ:
                converter = AObjConverter(common_options)
                output_path = common_options.converted_path
            elif source_format == SourceFormat.AGEB:
                converter = AGebConverter(common_options)
                output_path = common_options.converted_path
            elif source_format == SourceFormat.OGR:
                converter = OgrConverter(common_options)
                output_path = common_options.converted_groups_path
            elif source_format == SourceFormat.GFX:
                converter = GfxConverter(common_options)
                output_path = common_options.converted_gfx_path
            elif source_format == SourceFormat.SBF:
                converter = SbfConverter(common_options)
                output_path = common_options.converted_sfx_path
            elif source_format == SourceFormat.ED3:
                converter = Ed3Converter(common_options)
                output_path = common_options.converted_scenes_path
            elif source_format == SourceFormat.BGF:
                converter = (
                    BgfGltfConverter(common_options)
                    if target_format == TargetFormat.GLTF
                    or target_format == TargetFormat.GLTF_STATIC
                    else BgfWavefrontConverter(common_options)
                )
                output_path = common_options.converted_objects_path
            else:
                continue

            output_paths.extend(
                converter.convert(
                    file_paths,
                    output_path,
                    base_path,
                    source_format,
                    target_format,
                    create_subdirectories,
                )
            )
