from abc import ABC, abstractmethod
from pathlib import Path

from europa_1400_tools.const import TXS_EXTENSION, TargetFormat
from europa_1400_tools.construct.bgf import Bgf
from europa_1400_tools.construct.txs import Txs
from europa_1400_tools.converter.base_converter import BaseConverter
from europa_1400_tools.converter.common import Texture
from europa_1400_tools.extractor.commands import extract_file
from europa_1400_tools.helpers import rebase_path


class BgfConverter(BaseConverter, ABC):
    """Converter for BGF files."""

    extracted_texture_paths: list[Path]
    extracted_texture_names: list[str]

    def __init__(
        self,
        common_options,
    ):
        super().__init__(common_options)

        self.extracted_texture_paths = extract_file(
            self.common_options.game_textures_path,
            self.common_options.extracted_textures_path,
        )

        self.extracted_texture_names = [
            texture_path.stem for texture_path in self.extracted_texture_paths
        ]

    def convert_file(
        self,
        file_path: Path,
        output_path: Path,
        base_path: Path,
        target_format: TargetFormat,
        create_subdirectories: bool = False,
    ) -> list[Path]:
        output_sub_path: Path = rebase_path(
            file_path.parent, base_path, output_path / target_format.value[0]
        )

        if not output_sub_path.exists():
            output_sub_path.mkdir(parents=True)

        bgf = Bgf.from_file(file_path)

        txs_file_path = file_path.with_suffix(TXS_EXTENSION)
        txs: Txs | None = None

        if txs_file_path.exists():
            txs = Txs.from_file(txs_file_path)

        textures: list[Texture] = [
            Texture(bgf_texture, txs, self.extracted_texture_paths, self.common_options)
            for bgf_texture in bgf.textures
        ]

        return self.convert_bgf_file(
            bgf,
            output_sub_path,
            target_format,
            textures,
        )

    @abstractmethod
    def convert_bgf_file(
        self,
        bgf: Bgf,
        output_path: Path,
        target_format: TargetFormat,
        textures: list[Texture],
    ) -> list[Path]:
        """Convert BGF file and export to output_path."""
