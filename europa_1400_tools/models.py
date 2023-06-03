from dataclasses import dataclass
from pathlib import Path

from europa_1400_tools.const import EXTRACTED_DIR, RESOURCES_DIR


@dataclass
class CommonOptions:
    """Common options."""

    game_path: Path
    output_path: Path

    @property
    def resources_path(self) -> Path:
        """Return the path to the resources directory."""
        return self.game_path / RESOURCES_DIR

    @property
    def extracted_path(self) -> Path:
        """Return the path to the extracted directory."""
        return self.output_path / EXTRACTED_DIR
