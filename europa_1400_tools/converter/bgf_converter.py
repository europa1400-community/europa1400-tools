import pickle
from abc import ABC, abstractmethod
from pathlib import Path

import typer

from europa_1400_tools.common_options import CommonOptions
from europa_1400_tools.const import TXS_EXTENSION, TargetFormat
from europa_1400_tools.construct.bgf import Bgf
from europa_1400_tools.construct.txs import Txs
from europa_1400_tools.converter.base_converter import BaseConverter, ConstructType
from europa_1400_tools.decoder.bgf_decoder import BgfDecoder
from europa_1400_tools.decoder.txs_decoder import TxsDecoder
from europa_1400_tools.extractor.file_extractor import FileExtractor
from europa_1400_tools.helpers import rebase_path
from europa_1400_tools.preprocessor.objects_preprocessor import (
    ObjectMetadata,
    ObjectsPreprocessor,
)


class BgfConverter(BaseConverter, ABC):
    """Converter for BGF files."""

    object_metadatas: list[ObjectMetadata]

    def __init__(
        self,
        common_options: CommonOptions,
    ):
        super().__init__(common_options, Bgf, BgfDecoder)

        # self.extracted_texture_names = [
        #     texture_path.stem for texture_path in self.extracted_texture_paths
        # ]

    def preprocess(self, file_paths: list[Path]) -> None:
        file_extractor = FileExtractor(self.common_options)
        texture_paths = file_extractor.extract(
            self.common_options.game_textures_path,
            self.common_options.extracted_textures_path,
        )

        txs_decoder = TxsDecoder(self.common_options)
        txs_pickle_paths = txs_decoder.decode_files()

        objects_preprocessor = ObjectsPreprocessor(self.common_options)
        self.object_metadatas = objects_preprocessor.preprocess_objects(
            texture_paths,
            file_paths,
            txs_pickle_paths,
        )

    def convert(
        self,
        value: ConstructType,
        output_path: Path,
    ) -> list[Path]:
        return self._convert(
            value,
            output_path,
        )

    @abstractmethod
    def _convert(
        self,
        bgf: Bgf,
        output_path: Path,
    ) -> list[Path]:
        """Convert BGF and export to output_path."""
