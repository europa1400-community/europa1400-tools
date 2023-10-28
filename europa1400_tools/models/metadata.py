from dataclasses import dataclass, field
from pathlib import Path

from dataclasses_json import config, dataclass_json


@dataclass_json
@dataclass
class AnimationMetadata:
    """Metadata for an animation."""

    name: str
    path: Path = field(
        metadata=config(
            encoder=lambda path: str(path),
            decoder=lambda path: Path(path),
        )
    )
    vertices_count: int


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
    path: Path = field(
        metadata=config(
            encoder=lambda path: str(path),
            decoder=lambda path: Path(path),
        )
    )
    textures: list[TextureMetadata]
    animations: list[AnimationMetadata]
    txs_path: Path | None = field(
        metadata=config(
            encoder=lambda path: str(path) if path is not None else None,
            decoder=lambda path: Path(path) if path is not None else None,
        )
    )
