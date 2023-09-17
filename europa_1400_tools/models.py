"""Models for the Europa 1400 tools."""

from abc import ABC
from dataclasses import dataclass
from pathlib import Path

from europa_1400_tools.const import (
    A_GEB_DAT,
    A_OBJ_DAT,
    ANIMATIONS_BIN,
    CONVERTED_DIR,
    DATA_DIR,
    DECODED_DIR,
    EXTRACTED_DIR,
    GFX_DIR,
    GILDE_ADD_ON_GERMAN_GFX,
    GROUPS_BIN,
    MAPPED_ANIMATONS_PICKLE,
    OBJECTS_BIN,
    OUTPUT_ANIMATIONS_DIR,
    OUTPUT_GFX_DIR,
    OUTPUT_GROUPS_DIR,
    OUTPUT_OBJECTS_DIR,
    OUTPUT_SCENES_DIR,
    OUTPUT_SFX_DIR,
    OUTPUT_TEXTURES_DIR,
    RESOURCES_DIR,
    SCENES_BIN,
    SFX_DIR,
    TEXTURES_BIN,
)


@dataclass
class CommonOptions:
    """Common options."""

    game_path: Path
    output_path: Path
    verbose: bool

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
    def game_ageb_path(self) -> Path:
        """Return the path to the A_Geb file."""
        return self.game_data_path / A_GEB_DAT

    @property
    def game_aobj_path(self) -> Path:
        """Return the path to the A_Obj file."""
        return self.game_data_path / A_OBJ_DAT

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
    def game_gfx_path(self) -> Path:
        """Return the path to the game gfx directory."""
        return self.game_path / GFX_DIR / GILDE_ADD_ON_GERMAN_GFX

    @property
    def converted_gfx_path(self) -> Path:
        """Return the path to the converted gfx directory."""
        return self.converted_path / OUTPUT_GFX_DIR

    @property
    def game_sfx_path(self) -> Path:
        """Return the path to the game sfx directory."""
        return self.game_path / SFX_DIR

    @property
    def converted_sfx_path(self) -> Path:
        """Return the path to the converted sfx directory."""
        return self.converted_path / OUTPUT_SFX_DIR

    @property
    def game_scenes_path(self) -> Path:
        """Return the path to the game scenes directory."""
        return self.game_resources_path / SCENES_BIN

    @property
    def converted_scenes_path(self) -> Path:
        """Return the path to the converted scenes directory."""
        return self.converted_path / OUTPUT_SCENES_DIR

    @property
    def game_groups_path(self) -> Path:
        """Return the path to the game groups directory."""
        return self.game_resources_path / GROUPS_BIN

    @property
    def converted_groups_path(self) -> Path:
        """Return the path to the converted groups directory."""
        return self.converted_path / OUTPUT_GROUPS_DIR


@dataclass
class VertexJson:
    """Vertex in JSON format."""

    x: float
    y: float
    z: float


@dataclass
class OgrTransformJson:
    """OGR element data in JSON format."""

    position: VertexJson
    rotation: VertexJson


@dataclass
class OgrElementJson(ABC):
    """OGR element in JSON format."""

    name: str
    type: str


@dataclass
class OgrObjectElementJson(OgrElementJson):
    """OGR object element in JSON format."""

    object_name: str
    transform: OgrTransformJson
    additional_transform: OgrTransformJson | None


@dataclass
class OgrDummyElementJson(OgrElementJson):
    """OGR dummy element in JSON format."""

    transform: OgrTransformJson


@dataclass
class OgrLightBlockJson:
    """OGR light block in JSON format."""

    values: list[float]


@dataclass
class OgrLightElementJson(OgrElementJson):
    """OGR light element in JSON format."""

    blocks: list[OgrLightBlockJson]


@dataclass
class OgrJson:
    """OGR in JSON format."""

    name: str
    elements: list[OgrElementJson]
