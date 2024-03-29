import pickle
from abc import ABC, abstractmethod
from pathlib import Path

import typer

from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.cli.convert_options import ConvertOptions
from europa1400_tools.const import TXS_EXTENSION, TargetFormat
from europa1400_tools.construct.bgf import Bgf
from europa1400_tools.construct.txs import Txs
from europa1400_tools.converter.base_converter import BaseConverter, ConstructType
from europa1400_tools.decoder.baf_decoder import BafDecoder
from europa1400_tools.decoder.bgf_decoder import BgfDecoder
from europa1400_tools.decoder.txs_decoder import TxsDecoder
from europa1400_tools.extractor.file_extractor import FileExtractor
from europa1400_tools.helpers import rebase_path
from europa1400_tools.preprocessor.animations_preprocessor import (
    AnimationsPreprocessor,
)
from europa1400_tools.preprocessor.objects_preprocessor import (
    ObjectMetadata,
    ObjectsPreprocessor,
)


class BgfConverter(BaseConverter, ABC):
    """Converter for BGF files."""

    object_metadatas: list[ObjectMetadata]

    def __init__(self):
        super().__init__(Bgf, BgfDecoder)

    @property
    def decoded_path(self) -> Path:
        return ConvertOptions.instance.decoded_objects_path

    @property
    def converted_path(self) -> Path:
        return (
            ConvertOptions.instance.converted_objects_path
            / ConvertOptions.instance.target_format.value[0]
        )

    def preprocess(self, pickle_file_paths: list[Path]) -> None:
        file_extractor = FileExtractor()

        baf_decoder = BafDecoder()
        animations_pickle_paths = baf_decoder.decode_files()

        animations_preprocessor = AnimationsPreprocessor()
        animation_metadatas = animations_preprocessor.preprocess_animations(
            animations_pickle_paths
        )

        texture_paths = file_extractor.extract(
            ConvertOptions.instance.game_textures_path,
            ConvertOptions.instance.extracted_textures_path,
        )

        txs_file_paths = [
            file_path.relative_to(
                ConvertOptions.instance.decoded_objects_path
            ).with_suffix(TXS_EXTENSION)
            for file_path in pickle_file_paths
        ]
        txs_decoder = TxsDecoder()
        txs_pickle_file_paths = txs_decoder.decode_files(txs_file_paths)

        objects_preprocessor = ObjectsPreprocessor()
        self.object_metadatas = objects_preprocessor.preprocess_objects(
            texture_paths, pickle_file_paths, txs_pickle_file_paths, animation_metadatas
        )

    def convert(
        self,
        value: ConstructType,
        output_path: Path,
    ) -> list[Path]:
        object_metadata: ObjectMetadata | None = next(
            (
                object_metadata
                for object_metadata in self.object_metadatas
                if object_metadata.path == value.path
            ),
            None,
        )

        if object_metadata is None:
            raise ValueError(f"no metadata found for {value.name}")

        return self._convert(
            value,
            output_path,
            object_metadata,
        )

    @abstractmethod
    def _convert(
        self,
        bgf: Bgf,
        output_path: Path,
    ) -> list[Path]:
        """Convert BGF and export to output_path."""
