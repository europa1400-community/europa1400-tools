"""Constants for the europa1400_tools package."""

from enum import Enum, IntEnum

from europa1400_tools.models.gilde_path import GildePath

# Game Directories and Files

DATA_DIR = "Data"
GAME_DATA_PATH = GildePath(DATA_DIR)
GAME_A_GEB_DAT = "A_Geb.dat"
GAME_DATA_AGEB_DAT_PATH = GAME_DATA_PATH / GAME_A_GEB_DAT
GAME_A_OBJ_DAT = "A_Obj.dat"
GAME_DATA_AOBJ_DAT_PATH = GAME_DATA_PATH / GAME_A_OBJ_DAT
GAME_CHARACTER_NAMES_DAT = "character_names.dat"
GAME_NO_COMPRESSION_INI = "no_compression.ini"

GFX_DIR = "gfx"
GAME_GFX_PATH = GildePath(GFX_DIR)
BMP_DIR = "Bmp"
GROUNDPLANS_DIR = "GroundPlans"
MAPS_DIR = "Maps"
CHARACTER_NAMES_DAT = "character_names.dat"
GILDE_ADD_ON_GERMAN_GFX = "Gilde_add_on_german.gfx"
GILDE_ADD_ON_GERMAN_GFX_PATH = GAME_GFX_PATH / GILDE_ADD_ON_GERMAN_GFX
NO_COMPRESSION_INI = "no_compression.ini"

MOVIE_DIR = "Movie"
MSX_DIR = "msx"

RESOURCES_DIR = "Resources"
RESOURCES_PATH = GildePath(RESOURCES_DIR)
ANIMATIONS_BIN = "animations.bin"
GAME_RESOURCES_ANIMATIONS_BIN_PATH = RESOURCES_PATH / ANIMATIONS_BIN
FORMS_BIN0 = "forms.bin0"
GAME_RESOURCES_FORMS_BIN0_PATH = RESOURCES_PATH / FORMS_BIN0
GROUPS_BIN = "groups.bin"
GAME_RESOURCES_GROUPS_BIN_PATH = RESOURCES_PATH / GROUPS_BIN
OBJECTS_BIN = "objects.bin"
GAME_RESOURCES_OBJECTS_BIN_PATH = RESOURCES_PATH / OBJECTS_BIN
SCENES_BIN = "scenes.bin"
GAME_RESOURCES_SCENES_BIN_PATH = RESOURCES_PATH / SCENES_BIN
SCRIPTS_BIN = "scripts.bin"
GAME_RESOURCES_SCRIPTS_BIN_PATH = RESOURCES_PATH / SCRIPTS_BIN
SCRIPTS_BIN1 = "scripts.bin1"
GAME_RESOURCES_SCRIPTS_BIN1_PATH = RESOURCES_PATH / SCRIPTS_BIN1
TEXTBIN_GERMAN_BIN = "textbin_german.bin"
GAME_RESOURCES_TEXTBIN_GERMAN_BIN_PATH = RESOURCES_PATH / TEXTBIN_GERMAN_BIN
TEXTURES_BIN = "textures.bin"
GAME_RESOURCES_TEXTURES_BIN_PATH = RESOURCES_PATH / TEXTURES_BIN

SERVER_DIR = "server"

SFX_DIR = "sfx"
GAME_SFX_PATH = GildePath(SFX_DIR)

AI_METHOD_ADDON_INI = "ai_method_addon.ini"
ALCHEMY_DATA_INI = "alchemy_data.ini"
DIE_GILDE_ADD_ON_TEXT_DEF = "die_gilde_add_on_text.def"
GAME_INI = "game.ini"
GILDEGOLD_EXE = "GildeGold.exe"
GILDEGOLD_TL_EXE = "GildeGold_TL.exe"
INCLUDE_SFX_INI = "include_sfx.ini"
MOVEAHEAD_DLL = "moveahead.dll"

# Directory and File Categories

BIN_FILES = [
    GAME_RESOURCES_ANIMATIONS_BIN_PATH,
    GAME_RESOURCES_FORMS_BIN0_PATH,
    GAME_RESOURCES_GROUPS_BIN_PATH,
    GAME_RESOURCES_OBJECTS_BIN_PATH,
    GAME_RESOURCES_SCENES_BIN_PATH,
    GAME_RESOURCES_SCRIPTS_BIN_PATH,
    GAME_RESOURCES_FORMS_BIN0_PATH,
    GAME_RESOURCES_TEXTBIN_GERMAN_BIN_PATH,
    GAME_RESOURCES_TEXTURES_BIN_PATH,
]

CONVERTIBLE_PATHS = [
    GAME_DATA_AOBJ_DAT_PATH,
    GAME_DATA_AGEB_DAT_PATH,
    GILDE_ADD_ON_GERMAN_GFX_PATH,
    GAME_RESOURCES_GROUPS_BIN_PATH,
    GAME_RESOURCES_OBJECTS_BIN_PATH,
    GAME_RESOURCES_SCENES_BIN_PATH,
    GAME_SFX_PATH,
]

# Output Directories and Files

EXTRACTED_DIR = "extracted"
DECODED_DIR = "decoded"
CONVERTED_DIR = "converted"
OUTPUT_AGEB_DIR = "ageb"
OUTPUT_AOBJ_DIR = "aobj"
OUTPUT_SFX_DIR = "sfx"
OUTPUT_GFX_DIR = "gfx"
OUTPUT_GROUPS_DIR = "groups"
OUTPUT_ANIMATIONS_DIR = "animations"
OUTPUT_SCENES_DIR = "scenes"
OUTPUT_OBJECTS_DIR = "objects"
OUTPUT_TXS_DIR = "txs"
OUTPUT_TEXTURES_DIR = "textures"
OUTPUT_META_DIR = "meta"
OUTPUT_FORMS_DIR = "forms"
OUTPUT_SCRIPTS_DIR = "scripts"
OUTPUT_TEXTS_DIR = "texts"
MAPPED_ANIMATONS_PICKLE = "mapped_animations.pickle"
MISSING_PATHS_TXT = "missing_paths.txt"
AGEB_PICKLE = "ageb.pickle"
AGEB_JSON = GildePath("ageb.json")
AOBJ_PICKLE = "aobj.pickle"
AOBJ_JSON = "aobj.json"
GFX_PICKLE = "gfx.pickle"

# Target Format Output Directories

OUTPUT_WAV_DIR = "wav"
OUTPUT_MP3_DIR = "mp3"
OUTPUT_WAVEFRONT_DIR = "wavefront"
OUTPUT_GLTF_DIR = "gltf"
OUTPUT_GLTF_STATIC_DIR = "gltf-static"
OUTPUT_JSON_DIR = "json"
OUTPUT_PNG_DIR = "png"

# Commands

BAF_COMMAND = "baf"
AOBJ_COMMAND = "aobj"
AGEB_COMMAND = "ageb"
GFX_COMMAND = "gfx"
OGR_COMMAND = "ogr"
OGR_LFS_COMMAND = "ogr-lfs"
ED3_COMMAND = "ed3"
BGF_COMMAND = "bgf"
SBF_COMMAND = "sbf"
TXS_COMMAND = "txs"
FORM_COMMAND = "form"
ESC_COMMAND = "esc"
RES_COMMAND = "res"
BMP_COMMAND = "bmp"
WAV_COMMAND = "wav"
MP3_COMMAND = "mp3"
WAVEFRONT_COMMAND = "wavefront"
GLTF_COMMAND = "gltf"
GLTF_STATIC_COMMAND = "gltf-static"
JSON_COMMAND = "json"
PNG_COMMAND = "png"
BAF_INI_COMMAND = "baf-ini"
BAF_OAM_COMMAND = "baf-oam"

# File Extensions

BGF_EXTENSION = ".bgf"
OBJ_EXTENSION = ".obj"
MTL_EXTENSION = ".mtl"
BAF_EXTENSION = ".baf"
GLTF_EXTENSION = ".gltf"
GLB_EXTENSION = ".glb"
PNG_EXTENSION = ".png"
INI_EXTENSION = ".ini"
SBF_EXTENSION = ".sbf"
PICKLE_EXTENSION = ".pickle"
WAV_EXTENSION = ".wav"
MP3_EXTENSION = ".mp3"
GFX_EXTENSION = ".gfx"
LFS_EXTENSION = ".lfs"
OGR_EXTENSION = ".ogr"
JSON_EXTENSION = ".json"
OAM_EXTENSION = ".oam"
ED3_EXTENSION = ".ed3"
TXS_EXTENSION = ".txs"
DAT_EXTENSION = ".dat"
BIN_EXTENSION = ".bin"
TXT_EXTENSION = ".txt"
BMP_EXTENSION = ".bmp"
FORM_EXTENSION = ".form"
ESC_EXTENSION = ".esc"
RES_EXTENSION = ".res"

IGNORED_EXTENSIONS = [
    LFS_EXTENSION,
    TXT_EXTENSION,
]

# Construct


class SoundbankType(IntEnum):
    """Soundbank types."""

    SINGLE = 1
    MULTI = 2


class SoundType(IntEnum):
    """Sbf types."""

    WAV = 1
    MP3 = 2


# Converter


class Format(Enum):
    """Formats."""

    def __str__(self) -> str:
        return self.value[0]

    @property
    def extension(self) -> str:
        return self.value[1]


class OgrElementType(Enum):
    """Ogr element types."""

    OBJECT = "object"
    LIGHT = "light"
    DUMMY = "dummy"


BGF_DIR = "bgf"
OBJ_DIR = "obj"
TEX_DIR = "tex"
GLTF_DIR = "gltf"
BAF_DIR = "baf"

OBJECTS_STRING_ENCODING = "latin-1"

MODELS_REDUCED_FOOTER_FILES = [
    "ob_DREIFACHGALGEN.bgf",
    "ob_DREIFACKREUZ.bgf",
    "ob_EXEKUTIONSKANONESTOPFER.bgf",
]

WAVEFRONT_ENCODING = "utf-8"

BAF_INI_FILE_SECTION = "4HEAD Studios Animation-Settings"
BAF_INI_FILE_NUM_KEYS = "NumKeys"
BAF_INI_FILE_KEYS = "Keys"
BAF_INI_FILE_LOOP_IN = "LoopIn"
BAF_INI_FILE_LOOP_OUT = "LoopOut"


DEFAULT_OUTPUT_PATH = "output"


LATIN1_VALUES: list[int] = list(range(0x20, 0x7F)) + list(range(0xA0, 0x100))
