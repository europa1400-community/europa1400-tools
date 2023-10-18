# from dataclasses import dataclass
# from pathlib import Path

# from europa_1400_tools.common_options import CommonOptions
# from europa_1400_tools.const import PNG_EXTENSION
# from europa_1400_tools.construct.bgf import BgfTexture
# from europa_1400_tools.construct.txs import Txs
# from europa_1400_tools.helpers import strip_non_ascii
# from europa_1400_tools.preprocessor.textures_preprocessor import (
#     convert_bmp_to_png_with_transparency,
#     create_dummy_texture,
# )


# @dataclass
# class Texture:
#     bgf_texture: BgfTexture
#     txs: Txs | None
#     file_name_to_file_path: dict[str, Path]
#     main_texture_name: str
#     main_texture_path: Path
#     is_texture_path: bool
#     has_alpha: bool
#     has_txs: bool
#     common_options: CommonOptions

#     def __init__(
#         self,
#         bgf_texture: BgfTexture,
#         txs: Txs | None,
#         texture_paths: list[Path],
#         common_options: CommonOptions,
#     ):
#         self.bgf_texture = bgf_texture
#         self.txs = txs
#         self.common_options = common_options

#         texture_paths_normalized = [
#             texture_path.with_name(
#                 strip_non_ascii(texture_path.stem.lower()) + texture_path.suffix.lower()
#             )
#             for texture_path in texture_paths
#         ]
#         texture_names_normalized = [
#             texture_path_normalized.stem
#             for texture_path_normalized in texture_paths_normalized
#         ]

#         self.is_texture_path: bool = (
#             self.bgf_texture.name_normalized in texture_names_normalized
#         )
#         self.has_alpha: bool = self.bgf_texture.num0B != 0
#         self.has_txs: bool = self.txs is not None and len(self.txs.texture_names) > 0

#         self.file_name_to_file_path: dict[str, Path] = {}
#         file_names: list[str]

#         if self.is_texture_path or not self.has_txs:
#             file_names = [self.bgf_texture.name]
#         else:
#             file_names = self.txs.texture_names

#         file_names_normalized = [
#             strip_non_ascii(file_name.lower()) for file_name in file_names
#         ]

#         for i, file_name in enumerate(file_names):
#             file_name_normalized = file_names_normalized[i]
#             file_path: Path | None = next(
#                 (
#                     texture_path
#                     for j, texture_path in enumerate(texture_paths)
#                     if texture_paths_normalized[j].stem
#                     == Path(file_name_normalized).stem
#                 ),
#                 None,
#             )

#             if file_path is None:
#                 png_file_path = common_options.extracted_textures_path / Path(
#                     file_name
#                 ).with_suffix(PNG_EXTENSION)
#                 create_dummy_texture(png_file_path)
#                 file_name = png_file_path.name
#                 file_path = png_file_path

#             elif self.has_alpha:
#                 png_file_path = common_options.extracted_textures_path / Path(
#                     file_name
#                 ).with_suffix(PNG_EXTENSION)
#                 convert_bmp_to_png_with_transparency(file_path, png_file_path)
#                 file_name = png_file_path.name
#                 file_path = png_file_path

#             self.file_name_to_file_path[file_name] = file_path
#             self.main_texture_name, self.main_texture_path = list(
#                 self.file_name_to_file_path.items()
#             )[0]
