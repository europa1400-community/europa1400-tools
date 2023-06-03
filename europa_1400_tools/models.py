"""Models for the Europa 1400 tools."""

from dataclasses import dataclass
from pathlib import Path

from europa_1400_tools.const import DECODED_DIR, EXTRACTED_DIR, RESOURCES_DIR, SFX_DIR


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
