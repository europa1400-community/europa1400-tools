from dataclasses import dataclass, field
from pathlib import Path

from dataclasses_json import DataClassJsonMixin, config


@dataclass
class AnimationMetadata(DataClassJsonMixin):
    """Metadata for an animation."""

    name: str
    path: Path = field(
        metadata=config(
            encoder=lambda path: str(path),
            decoder=lambda path: Path(path),
        )
    )
    vertices_count: int


@dataclass
class TextureMetadata(DataClassJsonMixin):
    """Metadata for a texture."""

    name: str
    path: Path = field(
        metadata=config(
            encoder=lambda path: str(path),
            decoder=lambda path: Path(path),
        )
    )
    has_transparency: bool


@dataclass
class ObjectMetadata(DataClassJsonMixin):
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
