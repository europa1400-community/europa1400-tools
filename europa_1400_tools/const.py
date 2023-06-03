"""Constants for the europa_1400_tools package."""

from pathlib import Path

# Game Directories and Files

DATA_DIR = "Data"
A_GEB_DAT = "A_GEB.DAT"
A_OBJ_DAT = "A_OBJ.DAT"

GFX_DIR = "GFX"
BMP_DIR = "Bmp"
GROUNDPLANS_DIR = "GroundPlans"
MAPS_DIR = "Maps"
CHARACTER_NAMES_DAT = "character_names.dat"
GILDE_ADD_ON_GERMAN_GFX = "Gilde_add_on_german.gfx"
NO_COMPRESSION_INI = "no_compression.ini"

MOVIE_DIR = "Movie"
MSX_DIR = "msx"

RESOURCES_DIR = "Resources"
ANIMATIONS_BIN = "animations.bin"
FORMS_BIN0 = "forms.bin0"
GROUPS_BIN = "groups.bin"
OBJECTS_BIN = "objects.bin"
SCENES_BIN = "scenes.bin"
SCRIPTS_BIN = "scripts.bin"
SCRIPTS_BIN1 = "scripts.bin1"
TEXBIN_GERMAN_BIN = "textbin_german.bin"
TEXTURES_BIN = "textures.bin"

SERVER_DIR = "server"

SFX_DIR = "sfx"

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
    ANIMATIONS_BIN,
    FORMS_BIN0,
    GROUPS_BIN,
    OBJECTS_BIN,
    SCENES_BIN,
    SCRIPTS_BIN,
    SCRIPTS_BIN1,
    TEXBIN_GERMAN_BIN,
    TEXTURES_BIN,
]

# Output Directories and Files

EXTRACTED_DIR = "extracted"

BGF_DIR = "bgf"
OBJ_DIR = "obj"
TEX_DIR = "tex"
GLTF_DIR = "gltf"
BAF_DIR = "baf"

MODELS_STRING_ENCODING = "latin-1"

MODELS_REDUCED_FOOTER_FILES = [
    "ob_DREIFACHGALGEN.bgf",
    "ob_DREIFACKREUZ.bgf",
    "ob_EXEKUTIONSKANONESTOPFER.bgf",
]

BGF_EXCLUDE: list[Path] = []
BAF_EXCLUDE: list[Path] = []

BGF_EXTENSION = ".bgf"
OBJ_EXTENSION = ".obj"
MTL_EXTENSION = ".mtl"
BAF_EXTENSION = ".baf"
GLTF_EXTENSION = ".gltf"
GLB_EXTENSION = ".glb"
PNG_EXTENSION = ".png"
INI_EXTENSION = ".ini"

WAVEFRONT_ENCODING = "utf-8"

BAF_INI_FILE_SECTION = "4HEAD Studios Animation-Settings"
BAF_INI_FILE_NUM_KEYS = "NumKeys"
BAF_INI_FILE_KEYS = "Keys"
BAF_INI_FILE_LOOP_IN = "LoopIn"
BAF_INI_FILE_LOOP_OUT = "LoopOut"


DEFAULT_OUTPUT_PATH = Path("output")
