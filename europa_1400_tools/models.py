"""Models for the Europa 1400 tools."""

from dataclasses import dataclass
from pathlib import Path

from europa_1400_tools.const import (
    A_GEB_DAT,
    A_OBJ_DAT,
    CONVERTED_DIR,
    DATA_DIR,
    DECODED_DIR,
    EXTRACTED_DIR,
    GFX_DIR,
    GILDE_ADD_ON_GERMAN_GFX,
    RESOURCES_DIR,
    SFX_DIR,
)


@dataclass
class CommonOptions:
    """Common options."""

    game_path: Path
    output_path: Path

    @property
    def resources_game_path(self) -> Path:
        """Return the path to the resources directory."""
        return self.game_path / RESOURCES_DIR

    @property
    def data_game_path(self) -> Path:
        """Return the path to the data directory."""
        return self.game_path / DATA_DIR

    @property
    def gfx_game_path(self) -> Path:
        """Return the path to the GFX directory."""

        return self.game_path / GFX_DIR / GILDE_ADD_ON_GERMAN_GFX

    @property
    def sfx_game_path(self) -> Path:
        """Return the path to the SFX directory."""

        return self.game_path / SFX_DIR

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
    def ageb_game_path(self) -> Path:
        """Return the path to the A_Geb file."""
        return self.data_game_path / A_GEB_DAT

    @property
    def aobj_game_path(self) -> Path:
        """Return the path to the A_Obj file."""
        return self.data_game_path / A_OBJ_DAT
