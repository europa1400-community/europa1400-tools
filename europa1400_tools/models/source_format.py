from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Self

from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.const import (
    AGEB_COMMAND,
    AGEB_JSON,
    AOBJ_COMMAND,
    AOBJ_JSON,
    BAF_COMMAND,
    BAF_EXTENSION,
    BAF_INI_COMMAND,
    BAF_OAM_COMMAND,
    BGF_COMMAND,
    BGF_EXTENSION,
    BIN_EXTENSION,
    BMP_COMMAND,
    BMP_EXTENSION,
    DAT_EXTENSION,
    ED3_COMMAND,
    ED3_EXTENSION,
    ESC_COMMAND,
    ESC_EXTENSION,
    FORM_COMMAND,
    FORM_EXTENSION,
    GAME_A_GEB_DAT,
    GAME_A_OBJ_DAT,
    GAME_CHARACTER_NAMES_DAT,
    GAME_DATA_AGEB_DAT_PATH,
    GAME_DATA_AOBJ_DAT_PATH,
    GAME_DATA_PATH,
    GAME_GFX_PATH,
    GAME_NO_COMPRESSION_INI,
    GAME_RESOURCES_ANIMATIONS_BIN_PATH,
    GAME_RESOURCES_FORMS_BIN0_PATH,
    GAME_RESOURCES_GROUPS_BIN_PATH,
    GAME_RESOURCES_OBJECTS_BIN_PATH,
    GAME_RESOURCES_SCENES_BIN_PATH,
    GAME_RESOURCES_SCRIPTS_BIN1_PATH,
    GAME_RESOURCES_SCRIPTS_BIN_PATH,
    GAME_RESOURCES_TEXTBIN_GERMAN_BIN_PATH,
    GAME_RESOURCES_TEXTURES_BIN_PATH,
    GAME_SFX_PATH,
    GFX_COMMAND,
    GFX_EXTENSION,
    INI_EXTENSION,
    LFS_EXTENSION,
    OAM_EXTENSION,
    OGR_COMMAND,
    OGR_EXTENSION,
    OGR_LFS_COMMAND,
    OUTPUT_ANIMATIONS_DIR,
    OUTPUT_FORMS_DIR,
    OUTPUT_GFX_DIR,
    OUTPUT_GROUPS_DIR,
    OUTPUT_OBJECTS_DIR,
    OUTPUT_SCENES_DIR,
    OUTPUT_SCRIPTS_DIR,
    OUTPUT_SFX_DIR,
    OUTPUT_TEXTS_DIR,
    OUTPUT_TEXTURES_DIR,
    OUTPUT_TXS_DIR,
    PICKLE_EXTENSION,
    RES_COMMAND,
    RES_EXTENSION,
    SBF_COMMAND,
    SBF_EXTENSION,
    TXS_COMMAND,
    TXS_EXTENSION,
)
from europa1400_tools.construct.ageb import AGeb
from europa1400_tools.construct.aobj import AObj
from europa1400_tools.construct.baf import Baf
from europa1400_tools.construct.base_construct import BaseConstruct
from europa1400_tools.construct.bgf import Bgf
from europa1400_tools.construct.ed3 import Ed3
from europa1400_tools.construct.gfx import Gfx
from europa1400_tools.construct.ogr import Ogr
from europa1400_tools.construct.sbf import Sbf
from europa1400_tools.construct.txs import Txs
from europa1400_tools.models.gilde_path import GildePath
from europa1400_tools.models.target_format import TargetFormat, TargetFormats


class OutputFileMode(Enum):
    """Output file modes."""

    NONE = 0
    SINGLE_SOURCE_SINGLE_OUTPUT = 1
    SINGLE_SOURCE_MULTIPLE_OUTPUTS = 2
    MULTIPLE_SOURCES_SINGLE_OUTPUT = 3
    MULTIPLE_SOURCES_MULTIPLE_OUTPUTS = 4


@dataclass
class SourceFormat:
    """Source formats."""

    suffix: str
    target_formats: list[TargetFormat]
    command: str
    _source_paths: list[GildePath]
    output_path: GildePath
    is_single_source: bool = False
    is_single_output: bool = True
    construct_type: type[BaseConstruct] | None = None
    name: str | None = None

    @property
    def source_paths(self) -> list[GildePath]:
        return [
            CommonOptions.instance.game_path / source_path
            for source_path in self._source_paths
        ]

    @source_paths.setter
    def source_paths(self, values: list[GildePath]) -> None:
        self._source_paths = []

        for value in values:
            if not isinstance(value, GildePath):
                value = GildePath(value)

            if value.is_relative_to(CommonOptions.instance.game_path):
                value = value.relative_to(CommonOptions.instance.game_path)

            self._source_paths.append(value)

    @property
    def has_source_archive(self) -> bool:
        """Return whether the source format has a source archive."""

        return any(map(lambda value: value.is_archive, self.source_paths))

    @property
    def has_source_directory(self) -> bool:
        """Return whether the source format has a source directory."""

        return any(map(lambda value: value.is_dir(), self.source_paths))

    @property
    def has_source_file(self) -> bool:
        """Return whether the source format has a source file."""

        return any(map(lambda value: value.is_file(), self.source_paths))

    @property
    def source_archives(self) -> list[GildePath]:
        """Return the archives for the source format."""

        archives: list[GildePath] = []

        for source_path in self.source_paths:
            if source_path.is_archive:
                archives.append(source_path)

        return archives

    @property
    def source_directories(self) -> list[GildePath]:
        """Return the directories for the source format."""

        dirs: list[GildePath] = []

        for source_path in self.source_paths:
            if source_path.is_dir():
                dirs.append(source_path)

        return dirs

    @property
    def source_files(self) -> list[GildePath]:
        """Return the files for the source format."""

        files: list[GildePath] = []

        for source_path in self.source_paths:
            if source_path.is_file():
                files.append(source_path)

        return files

    @property
    def is_single_file(self) -> bool:
        """Return whether the source path is a single file."""

        for source_path in self.source_paths:
            if source_path.suffix == "":
                continue

            if source_path.has_suffix(self.suffix):
                continue

            return True

        return False

    def __hash__(self) -> int:
        return super().__hash__()

    @classmethod
    def from_path(cls, path: GildePath, source_path: Path | None = None) -> Self | None:
        """Return the source format for the given extension."""

        source_formats: list[SourceFormat] = [
            source_format.value for source_format in SourceFormats
        ]
        selected_source_format: SourceFormat | None = None

        if source_path is not None:
            matched_source_formats = [
                source_format
                for source_format in source_formats
                if any(
                    other_source_path.has_stem(source_path)
                    for other_source_path in source_format.source_paths
                )
            ]

            if len(matched_source_formats) > 0:
                source_formats = matched_source_formats

        named_source_formats = [
            source_format
            for source_format in source_formats
            if source_format.name is not None
        ]

        if any(named_source_formats):
            for source_format in named_source_formats:
                if path.has_name(source_format.name):
                    selected_source_format = source_format
                    break

            if selected_source_format is not None:
                return selected_source_format

        for source_format in source_formats:
            is_original_suffix = path.has_suffix(source_format.suffix)
            is_original_suffix_pickle = path.has_suffixes(
                [source_format.suffix, PICKLE_EXTENSION]
            )
            is_archive = path.is_archive
            is_main_source_file = len(source_format.source_paths) > 0 and path.has_name(
                source_format.source_paths[0]
            )
            is_source_name = any(
                path.has_name(source_path) for source_path in source_format.source_paths
            )

            if is_main_source_file or not is_archive and is_source_name:
                selected_source_format = source_format
                break

            if is_original_suffix:
                selected_source_format = source_format
                break

            if is_original_suffix_pickle:
                selected_source_format = source_format
                pass

        if selected_source_format is None:
            for source_format in source_formats:
                relative_paths = [
                    source_path.find(path) for source_path in source_format.source_paths
                ]
                if any(
                    [
                        source_path.find(path) is not None
                        for source_path in source_format.source_paths
                    ]
                ):
                    selected_source_format = source_format
                    break

        if selected_source_format is None:
            if path.can_shift_left:
                selected_source_format = cls.from_path(path.shift_left())

        return selected_source_format


class SourceFormats(Enum):
    """Source formats."""

    BAF: SourceFormat = SourceFormat(
        BAF_EXTENSION,
        [],
        BAF_COMMAND,
        [
            GAME_RESOURCES_ANIMATIONS_BIN_PATH,
        ],
        OUTPUT_ANIMATIONS_DIR,
        construct_type=Baf,
    )
    BGF: SourceFormat = SourceFormat(
        BGF_EXTENSION,
        [
            TargetFormats.WAVEFRONT,
            TargetFormats.GLTF,
            TargetFormats.GLTF_STATIC,
        ],
        BGF_COMMAND,
        [
            GAME_RESOURCES_OBJECTS_BIN_PATH,
            GAME_RESOURCES_SCENES_BIN_PATH,
        ],
        OUTPUT_OBJECTS_DIR,
        is_single_output=False,
        construct_type=Bgf,
    )
    GFX: SourceFormat = SourceFormat(
        GFX_EXTENSION,
        [
            TargetFormats.PNG,
        ],
        GFX_COMMAND,
        [
            GAME_GFX_PATH,
        ],
        OUTPUT_GFX_DIR,
        is_single_source=True,
        is_single_output=False,
        construct_type=Gfx,
    )
    SBF: SourceFormat = SourceFormat(
        SBF_EXTENSION,
        [
            TargetFormats.WAV,
            TargetFormats.MP3,
        ],
        SBF_COMMAND,
        [
            GAME_SFX_PATH,
        ],
        OUTPUT_SFX_DIR,
        is_single_output=False,
        construct_type=Sbf,
    )
    OGR: SourceFormat = SourceFormat(
        OGR_EXTENSION,
        [
            TargetFormats.JSON,
        ],
        OGR_COMMAND,
        [
            GAME_RESOURCES_GROUPS_BIN_PATH,
        ],
        OUTPUT_GROUPS_DIR,
        construct_type=Ogr,
    )
    ED3: SourceFormat = SourceFormat(
        ED3_EXTENSION,
        [
            TargetFormats.JSON,
        ],
        ED3_COMMAND,
        [
            GAME_RESOURCES_SCENES_BIN_PATH,
        ],
        OUTPUT_SCENES_DIR,
        construct_type=Ed3,
    )
    AOBJ: SourceFormat = SourceFormat(
        DAT_EXTENSION,
        [
            TargetFormats.JSON,
        ],
        AOBJ_COMMAND,
        [
            GAME_DATA_PATH,
        ],
        ".",
        name=GAME_A_OBJ_DAT,
        is_single_source=True,
        construct_type=AObj,
    )
    AGEB: SourceFormat = SourceFormat(
        DAT_EXTENSION,
        [
            TargetFormats.JSON,
        ],
        AGEB_COMMAND,
        [
            GAME_DATA_PATH,
        ],
        ".",
        name=GAME_A_GEB_DAT,
        is_single_source=True,
        construct_type=AGeb,
    )
    TXS: SourceFormat = SourceFormat(
        TXS_EXTENSION,
        [
            TargetFormats.JSON,
        ],
        TXS_COMMAND,
        [
            GAME_RESOURCES_OBJECTS_BIN_PATH,
        ],
        OUTPUT_TXS_DIR,
        construct_type=Txs,
    )
    FORM: SourceFormat = SourceFormat(
        FORM_EXTENSION,
        [
            TargetFormats.JSON,
        ],
        FORM_COMMAND,
        [
            GAME_RESOURCES_FORMS_BIN0_PATH,
        ],
        OUTPUT_FORMS_DIR,
    )
    ESC: SourceFormat = SourceFormat(
        ESC_EXTENSION,
        [
            TargetFormats.JSON,
        ],
        ESC_COMMAND,
        [
            GAME_RESOURCES_SCRIPTS_BIN_PATH,
            GAME_RESOURCES_SCRIPTS_BIN1_PATH,
        ],
        OUTPUT_SCRIPTS_DIR,
    )
    RES: SourceFormat = SourceFormat(
        RES_EXTENSION,
        [
            TargetFormats.JSON,
        ],
        RES_COMMAND,
        [
            GAME_RESOURCES_TEXTBIN_GERMAN_BIN_PATH,
        ],
        OUTPUT_TEXTS_DIR,
    )
    BMP: SourceFormat = SourceFormat(
        BMP_EXTENSION,
        [
            TargetFormats.PNG,
        ],
        BMP_COMMAND,
        [GAME_RESOURCES_TEXTURES_BIN_PATH, GAME_GFX_PATH],
        OUTPUT_TEXTURES_DIR,
    )
    BAF_INI: SourceFormat = SourceFormat(
        INI_EXTENSION,
        [],
        BAF_INI_COMMAND,
        [
            GAME_RESOURCES_ANIMATIONS_BIN_PATH,
        ],
        OUTPUT_ANIMATIONS_DIR,
    )
    BAF_OAM: SourceFormat = SourceFormat(
        OAM_EXTENSION,
        [],
        BAF_OAM_COMMAND,
        [
            GAME_RESOURCES_ANIMATIONS_BIN_PATH,
        ],
        OUTPUT_ANIMATIONS_DIR,
    )
    OGR_LFS: SourceFormat = SourceFormat(
        LFS_EXTENSION,
        [],
        OGR_LFS_COMMAND,
        [
            GAME_RESOURCES_GROUPS_BIN_PATH,
        ],
        OUTPUT_GROUPS_DIR,
    )
    CHARACTER_NAMES_DAT: SourceFormat = SourceFormat(
        DAT_EXTENSION,
        [],
        "",
        [
            GAME_GFX_PATH,
        ],
        ".",
        is_single_source=True,
        name=GAME_CHARACTER_NAMES_DAT,
    )
    NO_COMPRESSION_INI: SourceFormat = SourceFormat(
        INI_EXTENSION,
        [],
        "",
        [
            GAME_GFX_PATH,
        ],
        ".",
        name=GAME_NO_COMPRESSION_INI,
    )
