from dataclasses import dataclass
from enum import Enum
from typing import Union

from europa1400_tools.const import (
    GLTF_COMMAND,
    GLTF_EXTENSION,
    GLTF_STATIC_COMMAND,
    JSON_COMMAND,
    JSON_EXTENSION,
    MP3_COMMAND,
    MP3_EXTENSION,
    OBJ_EXTENSION,
    OUTPUT_GLTF_DIR,
    OUTPUT_GLTF_STATIC_DIR,
    OUTPUT_JSON_DIR,
    OUTPUT_MP3_DIR,
    OUTPUT_PNG_DIR,
    OUTPUT_WAV_DIR,
    OUTPUT_WAVEFRONT_DIR,
    PNG_COMMAND,
    PNG_EXTENSION,
    WAV_COMMAND,
    WAV_EXTENSION,
    WAVEFRONT_COMMAND,
)


class TyperTargetFormat(Enum):
    """Typer target formats."""

    WAV = "wav"
    MP3 = "mp3"
    WAVEFRONT = "wavefront"
    GLTF = "gltf"
    GLTF_STATIC = "gltf-static"
    JSON = "json"
    PNG = "png"


@dataclass
class TargetFormat:
    """Target format."""

    command: str
    extension: str
    output_path: str


class TargetFormats(Enum):
    """Target formats."""

    WAV: TargetFormat = TargetFormat(WAV_COMMAND, WAV_EXTENSION, OUTPUT_WAV_DIR)
    MP3: TargetFormat = TargetFormat(MP3_COMMAND, MP3_EXTENSION, OUTPUT_MP3_DIR)
    WAVEFRONT: TargetFormat = TargetFormat(
        WAVEFRONT_COMMAND, OBJ_EXTENSION, OUTPUT_WAVEFRONT_DIR
    )
    GLTF: TargetFormat = TargetFormat(GLTF_COMMAND, GLTF_EXTENSION, OUTPUT_GLTF_DIR)
    GLTF_STATIC: TargetFormat = TargetFormat(
        GLTF_STATIC_COMMAND, GLTF_EXTENSION, OUTPUT_GLTF_STATIC_DIR
    )
    JSON: TargetFormat = TargetFormat(JSON_COMMAND, JSON_EXTENSION, OUTPUT_JSON_DIR)
    PNG: TargetFormat = TargetFormat(PNG_COMMAND, PNG_EXTENSION, OUTPUT_PNG_DIR)

    @classmethod
    def convert_typer(cls):
        """Return an Enum type with values as the first elements of the tuples."""
        enum_dict = {format.name: format.value[0] for format in cls}
        return Enum("TyperTargetFormat", enum_dict)

    @staticmethod
    def from_typer(typer_target_format: str) -> Union["TargetFormat", None]:
        """Return the target format for the given typer target format."""

        for target_format in TargetFormats:
            if normalize(target_format.name) == normalize(typer_target_format):
                return target_format

        return None

    def to_typer(self) -> TyperTargetFormat | None:
        """Return the typer target format for the given target format."""

        for typer_target_format in TyperTargetFormat:
            if normalize(typer_target_format.name) == normalize(self.name):
                return typer_target_format

        return None
