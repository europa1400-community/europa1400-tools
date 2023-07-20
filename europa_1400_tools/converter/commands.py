"""Commands for converting files"""

from pathlib import Path
from typing import Annotated, List, Optional

import typer

from europa_1400_tools.const import (
    BIN_EXTENSION,
    CONVERTIBLE_PATHS,
    IGNORED_EXTENSIONS,
    OUTPUT_GFX_DIR,
    OUTPUT_GROUPS_DIR,
    OUTPUT_SCENES_DIR,
    OUTPUT_SFX_DIR,
    SourceFormat,
    TargetFormat,
)
from europa_1400_tools.converter.ageb_converter import AGebConverter
from europa_1400_tools.converter.aobj_converter import AObjConverter
from europa_1400_tools.converter.base_converter import BaseConverter
from europa_1400_tools.converter.ed3_converter import Ed3Converter
from europa_1400_tools.converter.gfx_converter import GfxConverter
from europa_1400_tools.converter.ogr_converter import OgrConverter
from europa_1400_tools.converter.sbf_converter import SbfConverter
from europa_1400_tools.extractor.commands import extract_file
from europa_1400_tools.helpers import get_files
from europa_1400_tools.logger import logger
from europa_1400_tools.models import CommonOptions

app = typer.Typer()


@app.callback(invoke_without_command=True)
def convert(
    ctx: typer.Context,
    paths: Annotated[List[Path], typer.Argument()] = None,
    target_format: Annotated[Optional[TargetFormat], typer.Option()] = None,
    create_subdirectories: Annotated[bool, typer.Option()] = False,
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
                base_path_to_file_paths[path] = []

            base_path_to_file_paths[path].append(path)

    format_to_file_paths: dict[SourceFormat, dict[Path, list[Path]]] = {}

    for base_path, file_paths in base_path_to_file_paths.items():
        for file_path in file_paths:
            if file_path.suffix.lower() in IGNORED_EXTENSIONS:
                continue

            source_format = SourceFormat.from_path(file_path)

            if source_format is None:
                logger.warning(f"Cannot convert {file_path.suffix} files")
                logger.warning(f"Skipping {file_path}")
                continue

            if source_format not in format_to_file_paths:
                format_to_file_paths[source_format] = {}

            if base_path not in format_to_file_paths[source_format]:
                format_to_file_paths[source_format][base_path] = []

            format_to_file_paths[source_format][base_path].append(file_path)

    for source_format, _base_path_to_file_paths in format_to_file_paths.items():
        for base_path, file_paths in _base_path_to_file_paths.items():
            _target_format = target_format

            if _target_format is None:
                _target_format = source_format.target_formats[0]

            if _target_format not in source_format.target_formats:
                logger.warning(
                    f"Cannot convert {source_format} files to {_target_format}"
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
                output_path = common_options.converted_path / OUTPUT_GROUPS_DIR
            elif source_format == SourceFormat.GFX:
                converter = GfxConverter(common_options)
                output_path = common_options.converted_path / OUTPUT_GFX_DIR
            elif source_format == SourceFormat.SBF:
                converter = SbfConverter(common_options)
                output_path = common_options.converted_path / OUTPUT_SFX_DIR
            elif source_format == SourceFormat.ED3:
                converter = Ed3Converter(common_options)
                output_path = common_options.converted_path / OUTPUT_SCENES_DIR
            else:
                continue

            converter.convert(
                file_paths,
                output_path,
                base_path,
                _target_format,
                create_subdirectories,
            )


# @app.command("all")
# def convert_all(ctx: typer.Context):
#     """Convert all files"""

#     convert_gfx(ctx)
#     convert_sfx(ctx)
#     convert_objects(ctx)
#     convert_groups(ctx)


# @app.command("objects")
# def convert_objects(
#     ctx: typer.Context,
#     target_object_format: Annotated[
#         TargetObjectFormat, typer.Option()
#     ] = TargetObjectFormat.GLTF.value,
#     file_paths: Annotated[
#         Optional[list[Path]],
#         typer.Option("--file", "-f", help=".bgf or .pickle files to convert."),
#     ] = None,
# ) -> list[Path]:
#     """Convert BGF files"""

#     common_options: CommonOptions = ctx.obj
#     converted_objects_path: Path = (
#         common_options.converted_path / OUTPUT_OBJECTS_DIR / target_object_format.value
#     )
#     output_file_paths: list[Path] = []

#     if not file_paths:
#         file_paths = decode_objects(ctx)

#     if file_paths is None:
#         typer.echo("No files to convert")
#         return output_file_paths

#     if not all(file_path.suffix == file_paths[0].suffix for file_path in file_paths):
#         raise ValueError("All files must have the same extension")

#     suffix = file_paths[0].suffix

#     if suffix not in [BGF_EXTENSION, PICKLE_EXTENSION]:
#         raise ValueError(f"Unknown file extension: {suffix}")

#     is_bgf: bool = suffix == BGF_EXTENSION

#     if is_bgf and len(file_paths) > 1:
#         raise ValueError("Can only convert one .bgf file at a time")

#     textures_bin_path = common_options.resources_game_path / TEXTURES_BIN
#     extracted_textures_path = common_options.extracted_path / textures_bin_path.stem
#     extract_file(textures_bin_path, extracted_textures_path)

#     if is_bgf:
#         file_paths = decode_objects(ctx)

#     load_time = time.time()
#     typer.echo(f"Loading {len(file_paths)} files")

#     bgfs: list[Bgf] = []

#     for file_path in file_paths:
#         with open(file_path, "rb") as pickle_file:
#             bgf: Bgf = pickle.load(pickle_file)

#         if common_options.verbose:
#             typer.echo(f"Loaded {file_path.name} in {time.time() - load_time:.2f}s")

#         bgfs.append(bgf)

#     convert_time = time.time()
#     typer.echo(f"Converting {len(bgfs)} objects...")

#     if target_object_format == TargetObjectFormat.GLTF:
#         _ = decode_animations(ctx)
#         decoded_animations_path = common_options.decoded_path / OUTPUT_ANIMATIONS_DIR
#         decoded_objects_path = common_options.decoded_path / OUTPUT_OBJECTS_DIR

#         mapped_animations_path = map_animations(
#             ctx, decoded_animations_path, decoded_objects_path
#         )

#         with open(mapped_animations_path, "rb") as pickle_file:
#             mapped_animations = pickle.load(pickle_file)

#     for i, bgf in enumerate(bgfs):
#         convert_shapebank_time = time.time()
#         file_path = file_paths[i]
#         name = file_path.stem

#         if common_options.verbose:
#             typer.echo(f"Converting {name}...")

#         output_file_path = rebase_path(
#             file_path, decoded_objects_path, converted_objects_path
#         ).parent / Path(name)

#         if target_object_format == TargetObjectFormat.WAVEFRONT:
#             ObjectWavefrontConverter.convert_and_export(
#                 bgf,
#                 output_file_path,
#                 path=file_path,
#                 extracted_textures_path=extracted_textures_path,
#             )
#         elif target_object_format == TargetObjectFormat.GLTF_STATIC:
#             ObjectGltfConverter.convert_and_export(
#                 bgf,
#                 output_file_path,
#                 path=file_path,
#                 extracted_textures_path=extracted_textures_path,
#                 name=name,
#             )
#         elif target_object_format == TargetObjectFormat.GLTF:
#             extracted_objects_path = common_options.extracted_path / OUTPUT_OBJECTS_DIR
#             extracted_animations_path = (
#                 common_options.extracted_path / OUTPUT_ANIMATIONS_DIR
#             )
#             stripped_bgf_path = bgf.path.relative_to(extracted_objects_path)

#             baf_path: Path | None = None
#             baf: Baf | None = None

#             for mapped_baf_path, mapped_bgf_paths in mapped_animations.items():
#                 if stripped_bgf_path in mapped_bgf_paths:
#                     baf_path = extracted_animations_path / mapped_baf_path
#                     break

#             if baf_path is not None:
#                 with open(baf_path, "rb") as pickle_file:
#                     baf = pickle.load(pickle_file)

#             ObjectGltfConverter.convert_and_export(
#                 bgf,
#                 output_file_path,
#                 path=file_path,
#                 extracted_textures_path=extracted_textures_path,
#                 name=name,
#                 baf=baf,
#             )
#         else:
#             raise ValueError(f"Unknown object format: {target_object_format}")

#         if common_options.verbose:
#             typer.echo(
#                 f"Converted {name} in {time.time() - convert_shapebank_time:.2f}s"
#             )

#         output_file_paths.append(output_file_path)

#     typer.echo(f"Converted {len(bgfs)} objects in {time.time() - convert_time:.2f}s")

#     return output_file_paths


# @app.command("groups")
# def convert_groups(
#     ctx: typer.Context,
#     file_paths: Annotated[
#         Optional[list[Path]],
#         typer.Option("--file", "-f", help=".ogr or .pickle files to convert."),
#     ] = None,
# ) -> list[Path]:
#     """Convert OGR files"""

#     common_options: CommonOptions = ctx.obj
#     output_file_paths: list[Path] = []

#     if not file_paths:
#         file_paths = decode_groups(ctx)

#     if not all(file_path.suffix == file_paths[0].suffix for file_path in file_paths):
#         raise ValueError("All files must have the same extension")

#     suffix = file_paths[0].suffix

#     if suffix not in [OGR_EXTENSION, PICKLE_EXTENSION]:
#         raise ValueError(f"Unknown file extension: {suffix}")

#     is_ogr: bool = suffix == OGR_EXTENSION

#     if is_ogr and len(file_paths) > 1:
#         raise ValueError("Can only convert one .ogr file at a time")

#     if is_ogr:
#         file_paths = decode_groups(ctx)

#     load_time = time.time()
#     typer.echo(f"Loading {len(file_paths)} files")

#     ogrs: list[Ogr] = []

#     for file_path in file_paths:
#         with open(file_path, "rb") as pickle_file:
#             ogr: Ogr = pickle.load(pickle_file)

#         if common_options.verbose:
#             typer.echo(f"Loaded {file_path.name} in {time.time() - load_time:.2f}s")

#         ogrs.append(ogr)

#     convert_time = time.time()
#     typer.echo(f"Converting {len(ogrs)} groups...")

#     for i, ogr in enumerate(ogrs):
#         convert_ogr_time = time.time()
#         file_path = file_paths[i]
#         name = file_path.stem

#         group_output_file_paths = OgrConverter.convert_and_export(
#             ogr, common_options.converted_path / OUTPUT_GROUPS_DIR, name=name
#         )

#         output_file_paths.extend(group_output_file_paths)

#         if common_options.verbose:
#             typer.echo(
#                 f"Converted {name} in " + f"{time.time() - convert_ogr_time:.2f}s"
#             )

#     typer.echo(f"Converted {len(ogrs)} groups in {time.time() - convert_time:.2f}s")

#     return output_file_paths


# @app.command("gfx")
# def convert_gfx(
#     ctx: typer.Context,
#     file_paths: Annotated[
#         Optional[list[Path]],
#         typer.Option("--file", "-f", help=".gfx file or .pickle files to convert."),
#     ] = None,
# ) -> list[Path]:
#     """Convert GFX file to PNG files"""

#     common_options: CommonOptions = ctx.obj
#     output_file_paths: list[Path] = []

#     if not file_paths:
#         file_paths = [common_options.gfx_game_path]

#     # check for mixed extensions
#     if not all(file_path.suffix == file_paths[0].suffix for file_path in file_paths):
#         raise ValueError("All files must have the same extension")

#     suffix = file_paths[0].suffix

#     if suffix not in [GFX_EXTENSION, PICKLE_EXTENSION]:
#         raise ValueError(f"Unknown file extension: {suffix}")

#     is_gfx: bool = suffix == GFX_EXTENSION

#     if is_gfx and len(file_paths) > 1:
#         raise ValueError("Can only convert one .gfx file at a time")

#     if is_gfx:
#         file_paths = decode_gfx(ctx, file_paths[0])

#     shapebank_definitions: list[ShapebankDefinition] = []

#     load_time = time.time()
#     typer.echo(f"Loading {len(file_paths)} files...")

#     for file_path in file_paths:
#         load_shapebank_time = time.time()

#         with open(file_path, "rb") as pickle_file:
#             shapebank_definition: ShapebankDefinition = pickle.load(pickle_file)

#         if common_options.verbose:
#             typer.echo(
#                 f"Loaded {shapebank_definition.name} in "
#                 + f"{time.time() - load_shapebank_time:.2f}s"
#             )

#         shapebank_definitions.append(shapebank_definition)

#     typer.echo(f"Loaded {len(file_paths)} files in {time.time() - load_time:.2f}s")

#     convert_time = time.time()
#     typer.echo(f"Converting {len(file_paths)} files...")

#     for shapebank_definition in shapebank_definitions:
#         convert_shapebank_time = time.time()

#         shapebank_output_file_paths = ShapebankConverter.convert_and_export(
#             shapebank_definition, common_options.converted_path / OUTPUT_GFX_DIR
#         )

#         output_file_paths.extend(shapebank_output_file_paths)

#         if common_options.verbose:
#             typer.echo(
#                 f"Converted {shapebank_definition.name} in "
#                 + f"{time.time() - convert_shapebank_time:.2f}s"
#             )

#     typer.echo(
#         f"Converted {len(file_paths)} files in {time.time() - convert_time:.2f}s"
#     )

#     return output_file_paths


# @app.command("sfx")
# def convert_sfx(
#     ctx: typer.Context,
#     target_audio_format: TargetAudioFormat = typer.Option(
#         default=TargetAudioFormat.WAV.value
#     ),
#     file_paths: Annotated[
#         Optional[list[Path]], typer.Option(help=".sbf or .pickle files to convert.")
#     ] = None,
# ) -> list[Path]:
#     """Convert SFX files to WAV and MP3 files"""

#     common_options: CommonOptions = ctx.obj
#     audio_output_paths: list[Path] = []
#     pickle_file_paths: list[Path] = []

#     if not file_paths:
#         pickle_file_paths = decode_sfx(ctx)

#         decoded_sfx_path = common_options.decoded_path / SFX_DIR
#         converted_sfx_path = common_options.converted_path / SFX_DIR

#         for pickle_file_path in pickle_file_paths:
#             typer.echo(f"Converting {pickle_file_path}...")

#             with open(pickle_file_path, "rb") as pickle_file:
#                 sbf: Sbf = pickle.load(pickle_file)

#             audio_output_path_parent = rebase_path(
#                 pickle_file_path.parent, decoded_sfx_path, converted_sfx_path
#             )
#             audio_output_paths = SbfConverter.convert_and_export(
#                 sbf, audio_output_path_parent, target_audio_format=target_audio_format
#             )
#             audio_output_paths.extend(audio_output_paths)

#         return audio_output_paths

#     for file_path in file_paths:
#         if file_path.suffix == SBF_EXTENSION:
#             pickle_file_paths.extend(decode_sfx(ctx, file_paths=[file_path]))
#         elif file_path.suffix == PICKLE_EXTENSION:
#             pickle_file_paths.append(file_path)
#         else:
#             raise ValueError(f"Unsupported file extension: {file_path.suffix}")

#     for pickle_file_path in pickle_file_paths:
#         typer.echo(f"Converting {pickle_file_path}...")

#         with open(pickle_file_path, "rb") as pickle_file:
#             sbf = pickle.load(pickle_file)

#         audio_output_paths = SbfConverter.convert_and_export(
#             sbf, converted_sfx_path, target_audio_format=target_audio_format
#         )
#         audio_output_paths.extend(audio_output_paths)

#     return audio_output_paths
