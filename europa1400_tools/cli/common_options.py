from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, ClassVar, Optional, Self

import typer

from europa1400_tools.const import (
    A_GEB_DAT,
    A_OBJ_DAT,
    AGEB_JSON,
    AGEB_PICKLE,
    ANIMATIONS_BIN,
    AOBJ_JSON,
    AOBJ_PICKLE,
    CONVERTED_DIR,
    DATA_DIR,
    DECODED_DIR,
    DEFAULT_OUTPUT_PATH,
    EXTRACTED_DIR,
    GFX_DIR,
    GFX_PICKLE,
    GILDE_ADD_ON_GERMAN_GFX,
    GROUPS_BIN,
    MAPPED_ANIMATONS_PICKLE,
    MISSING_PATHS_TXT,
    OBJECTS_BIN,
    OUTPUT_ANIMATIONS_DIR,
    OUTPUT_GFX_DIR,
    OUTPUT_GROUPS_DIR,
    OUTPUT_META_DIR,
    OUTPUT_OBJECTS_DIR,
    OUTPUT_SCENES_DIR,
    OUTPUT_SFX_DIR,
    OUTPUT_TEXTURES_DIR,
    OUTPUT_TXS_DIR,
    RESOURCES_DIR,
    SCENES_BIN,
    SFX_DIR,
    TEXTURES_BIN,
    TargetFormat,
)
from europa1400_tools.helpers import ask_for_game_path


@dataclass
class CommonOptions:
    """Dataclass defining CLI options used by all commands."""

    instance: ClassVar[Self]

    def __post_init__(self):
        CommonOptions.instance = self

    _game_path: Annotated[
        Optional[str],
        typer.Option(
            "--game-path",
            "-g",
            help="Path to the game directory.",
        ),
    ] = None
    _output_path: Annotated[
        str,
        typer.Option(
            "--output-path",
            "-o",
            help="Path to the output directory.",
        ),
    ] = str(DEFAULT_OUTPUT_PATH)
    use_cache: Annotated[
        bool, typer.Option("--use-cache", "-c", help="Use cached files.")
    ] = False
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Verbose output.")
    ] = False

    ATTRNAME: str = field(default="common_params", metadata={"ignore": True})

    @property
    def game_path(self) -> Path:
        """Return the path to the game directory."""

        if self._game_path is None:
            self._game_path = ask_for_game_path().as_posix()

        if self._game_path is None:
            raise ValueError("Game path is None")

        return Path(self._game_path).resolve()

    @property
    def output_path(self) -> Path:
        """Return the path to the output directory."""
        return Path(self._output_path).resolve()

    @classmethod
    def from_context(cls, ctx: typer.Context) -> "CommonOptions":
        if (common_params_dict := getattr(ctx, "common_params", None)) is None:
            raise ValueError("Context missing common_params")

        return cls(**common_params_dict)

    @property
    def game_resources_path(self) -> Path:
        """Return the path to the resources directory."""
        return self.game_path / RESOURCES_DIR

    @property
    def game_data_path(self) -> Path:
        """Return the path to the data directory."""
        return self.game_path / DATA_DIR

    @property
    def extracted_path(self) -> Path:
        """Return the path to the extracted directory."""
        return self.output_path / EXTRACTED_DIR

    @property
    def decoded_path(self) -> Path:
        """Return the path to the decoded directory."""
        return self.output_path / DECODED_DIR

    @property
    def converted_path(self) -> Path:
        """Return the path to the converted directory."""
        return self.output_path / CONVERTED_DIR

    @property
    def game_textures_path(self) -> Path:
        """Return the path to the textures file."""
        return self.game_resources_path / TEXTURES_BIN

    @property
    def extracted_textures_path(self) -> Path:
        """Return the path to the extracted textures directory."""
        return self.output_path / EXTRACTED_DIR / OUTPUT_TEXTURES_DIR

    @property
    def converted_textures_path(self) -> Path:
        """Return the path to the converted textures directory."""
        return self.output_path / CONVERTED_DIR / OUTPUT_TEXTURES_DIR

    @property
    def game_ageb_path(self) -> Path:
        """Return the path to the A_Geb file."""
        return self.game_data_path / A_GEB_DAT

    @property
    def decoded_ageb_path(self) -> Path:
        """Return the path to the decoded A_Geb file."""
        return self.decoded_path / AGEB_PICKLE

    @property
    def converted_ageb_path(self) -> Path:
        """Return the path to the converted A_Geb file."""
        return self.converted_path / AGEB_JSON

    @property
    def game_aobj_path(self) -> Path:
        """Return the path to the A_Obj file."""
        return self.game_data_path / A_OBJ_DAT

    @property
    def decoded_aobj_path(self) -> Path:
        """Return the path to the decoded A_Obj file."""
        return self.decoded_path / AOBJ_PICKLE

    @property
    def converted_aobj_path(self) -> Path:
        """Return the path to the converted A_Obj file."""
        return self.converted_path / AOBJ_JSON

    @property
    def game_objects_path(self) -> Path:
        """Return the path to the game objects directory."""
        return self.game_resources_path / OBJECTS_BIN

    @property
    def extracted_objects_path(self) -> Path:
        """Return the path to the extracted objects directory."""
        return self.extracted_path / OUTPUT_OBJECTS_DIR

    @property
    def decoded_objects_path(self) -> Path:
        """Return the path to the decoded objects directory."""
        return self.decoded_path / OUTPUT_OBJECTS_DIR

    @property
    def converted_objects_path(self) -> Path:
        """Return the path to the converted objects directory."""
        return self.converted_path / OUTPUT_OBJECTS_DIR

    @property
    def converted_objects_meta_path(self) -> Path:
        """Return the path to the converted objects directory."""
        return self.converted_objects_path / OUTPUT_META_DIR

    @property
    def converted_objects_wavefront_path(self) -> Path:
        """Return the path to the converted objects directory."""
        return self.converted_objects_path / TargetFormat.WAVEFRONT.value[0]

    @property
    def converted_objects_gltf_static_path(self) -> Path:
        """Return the path to the converted objects directory."""
        return self.converted_objects_path / TargetFormat.GLTF_STATIC.value[0]

    @property
    def converted_objects_gltf_path(self) -> Path:
        """Return the path to the converted objects directory."""
        return self.converted_objects_path / TargetFormat.GLTF.value[0]

    @property
    def extracted_txs_path(self) -> Path:
        """Return the path to the extracted txs directory."""
        return self.extracted_path / OUTPUT_TXS_DIR

    @property
    def decoded_txs_path(self) -> Path:
        """Return the path to the decoded txs directory."""
        return self.decoded_path / OUTPUT_TXS_DIR

    @property
    def converted_txs_path(self) -> Path:
        """Return the path to the decoded txs directory."""
        return self.converted_path / OUTPUT_TXS_DIR

    @property
    def game_animations_path(self) -> Path:
        """Return the path to the game animations directory."""
        return self.game_resources_path / ANIMATIONS_BIN

    @property
    def extracted_animations_path(self) -> Path:
        """Return the path to the extracted animations directory."""
        return self.extracted_path / OUTPUT_ANIMATIONS_DIR

    @property
    def decoded_animations_path(self) -> Path:
        """Return the path to the decoded animations directory."""
        return self.decoded_path / OUTPUT_ANIMATIONS_DIR

    @property
    def converted_animations_path(self) -> Path:
        """Return the path to the converted animations directory."""
        return self.converted_path / OUTPUT_ANIMATIONS_DIR

    @property
    def mapped_animations_path(self) -> Path:
        """Return the path to the mapped animations directory."""
        return self.output_path / MAPPED_ANIMATONS_PICKLE

    @property
    def missing_paths_path(self) -> Path:
        """Return the path to the missing paths file."""
        return self.output_path / MISSING_PATHS_TXT

    @property
    def game_gfx_path(self) -> Path:
        """Return the path to the game gfx file."""
        return self.game_path / GFX_DIR / GILDE_ADD_ON_GERMAN_GFX

    @property
    def decoded_gfx_path(self) -> Path:
        """Path to the decoded gfx file."""
        return self.decoded_path / GFX_DIR / GFX_PICKLE

    @property
    def converted_gfx_path(self) -> Path:
        """Return the path to the converted gfx directory."""
        return self.converted_path / OUTPUT_GFX_DIR

    @property
    def game_sfx_path(self) -> Path:
        """Return the path to the game sfx directory."""
        return self.game_path / SFX_DIR

    @property
    def extracted_sfx_path(self) -> Path:
        """Return the path to the extracted sfx directory."""
        return self.extracted_path / OUTPUT_SFX_DIR

    @property
    def decoded_sfx_path(self) -> Path:
        """Return the path to the decoded sfx directory."""
        return self.decoded_path / OUTPUT_SFX_DIR

    @property
    def converted_sfx_path(self) -> Path:
        """Return the path to the converted sfx directory."""
        return self.converted_path / OUTPUT_SFX_DIR

    @property
    def game_scenes_path(self) -> Path:
        """Return the path to the game scenes directory."""
        return self.game_resources_path / SCENES_BIN

    @property
    def extracted_scenes_path(self) -> Path:
        """Return the path to the extracted scenes directory."""
        return self.extracted_path / OUTPUT_SCENES_DIR

    @property
    def decoded_scenes_path(self) -> Path:
        """Return the path to the decoded scenes directory."""
        return self.decoded_path / OUTPUT_SCENES_DIR

    @property
    def converted_scenes_path(self) -> Path:
        """Return the path to the converted scenes directory."""
        return self.converted_path / OUTPUT_SCENES_DIR

    @property
    def game_groups_path(self) -> Path:
        """Return the path to the game groups directory."""
        return self.game_resources_path / GROUPS_BIN

    @property
    def extracted_groups_path(self) -> Path:
        """Return the path to the extracted groups directory."""
        return self.extracted_path / OUTPUT_GROUPS_DIR

    @property
    def decoded_groups_path(self) -> Path:
        """Return the path to the decoded groups directory."""
        return self.decoded_path / OUTPUT_GROUPS_DIR

    @property
    def converted_groups_path(self) -> Path:
        """Return the path to the converted groups directory."""
        return self.converted_path / OUTPUT_GROUPS_DIR
