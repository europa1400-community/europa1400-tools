"""Base class for converters."""

import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from timeit import default_timer as timer
from typing import Generic, Type, TypeVar, final

from europa1400_tools.cli.convert_options import ConvertOptions
from europa1400_tools.cli.file_options import FileOptions
from europa1400_tools.const import PICKLE_EXTENSION
from europa1400_tools.construct.base_construct import BaseConstruct
from europa1400_tools.models.gilde_file import GildeAsset
from europa1400_tools.rich.common import console
from europa1400_tools.rich.progress import Progress


class BaseConverter:
    """Base class for converters."""

    def convert_assets(self, assets: list[GildeAsset] | None = None) -> None:
        """Convert files."""

        if assets is None:
            assets = FileOptions.instance.files

        decoder = self.decoder_type()

        assets_to_decode: list[GildeAsset] = []

        for asset in assets:
            if not asset.decoded_path.exists():
                assets_to_decode.append(asset)

        decoder.decode_assets(assets_to_decode)

        self.preprocess(assets)

        progress = Progress(
            title=f"Converting {self.construct_type.__name__}",
            total_file_count=len(assets),
        )

        with progress:
            for asset in assets:
                with asset.decoded_path.open("rb") as file:
                    value: ConstructType = pickle.load(file)

                progress.file_path = asset.path

                if not asset.converted_path.exists():
                    asset.converted_path.parent.mkdir(parents=True, exist_ok=True)

                self.convert(value, asset.converted_path)

                progress.completed_file_count += 1

    @property
    def decoded_path(self) -> Path:
        """Return the decoded path."""

        return ConvertOptions.instance.decoded_path

    @property
    def converted_path(self) -> Path:
        """Return the converted path."""

        return ConvertOptions.instance.converted_path

    @property
    def is_single_output_file(self) -> bool:
        """Return whether the output is a single file."""

        return True

    def preprocess(
        self,
        file_paths: list[Path],
    ) -> None:
        """Preprocess files."""

    @abstractmethod
    def convert(
        self,
        value: BaseConstruct,
        output_path: Path,
    ) -> list[Path]:
        """Convert file and export to output_path."""
