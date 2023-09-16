from abc import ABC, abstractmethod
from pathlib import Path

from europa_1400_tools.const import TargetFormat
from europa_1400_tools.construct.bgf import Bgf
from europa_1400_tools.converter.base_converter import BaseConverter
from europa_1400_tools.extractor.commands import extract_file
from europa_1400_tools.helpers import rebase_path


class BgfConverter(BaseConverter, ABC):
    """Converter for BGF files."""

    extracted_texture_paths: list[Path]

    def __init__(
        self,
        common_options,
    ):
        super().__init__(common_options)

        self.extracted_textures_paths = extract_file(
            self.common_options.textures_bin_path,
            self.common_options.extracted_textures_path,
        )

    def convert_file(
        self,
        file_path: Path,
        output_path: Path,
        base_path: Path,
        target_format: TargetFormat,
        create_subdirectories: bool = False,
    ) -> list[Path]:
        output_sub_path: Path = rebase_path(file_path.parent, base_path, output_path)

        if not output_sub_path.exists():
            output_sub_path.mkdir(parents=True)

        return self.convert_bgf_file(
            file_path,
            output_sub_path,
            base_path,
            target_format,
            create_subdirectories,
        )

    @abstractmethod
    def convert_bgf_file(
        self,
        file_path: Path,
        output_path: Path,
        base_path: Path,
        target_format: TargetFormat,
        create_subdirectories: bool = False,
    ) -> list[Path]:
        """Convert BGF file and export to output_path."""
