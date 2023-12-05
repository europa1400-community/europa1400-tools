from dataclasses import dataclass
from pathlib import Path

import construct as cs
from construct_typed import DataclassMixin, DataclassStruct, csfield

from europa1400_tools.construct.baf import Vector3
from europa1400_tools.construct.base_construct import BaseConstruct
from europa1400_tools.construct.common import Skip0, SkipNonLatin1, ignoredcsfield


def skip_until(obj, ctx):
    if obj in ctx.acceptable_values:
        raise cs.CancelParsing


@dataclass
class SkipUntil28(DataclassMixin):
    """Structure of a skip_until_28 block."""

    acceptable_values: list[int] = csfield(cs.Computed(lambda ctx: [0x28]))
    skipped: list[int] = csfield(cs.GreedyRange(cs.Byte * skip_until))
    const_28: bytes = csfield(cs.Const(b"\x28"))


@dataclass
class Face(DataclassMixin):
    """Structure of face."""

    a: int = csfield(cs.Int32ul)
    b: int = csfield(cs.Int32ul)
    c: int = csfield(cs.Int32ul)


@dataclass
class TextureCoordinate(DataclassMixin):
    """Structure of texture coordinate."""

    u: float = csfield(cs.Float32l)
    v: float = csfield(cs.Float32l)
    w: float = csfield(cs.Float32l)


@dataclass
class TextureMapping(DataclassMixin):
    """Structure of texture mapping."""

    vertex_u: Vector3 = csfield(DataclassStruct(Vector3))
    vertex_v: Vector3 = csfield(DataclassStruct(Vector3))
    vertex_w: Vector3 = csfield(DataclassStruct(Vector3))

    a: TextureCoordinate = csfield(
        cs.Computed(
            lambda ctx: TextureCoordinate(
                ctx.vertex_u.x, ctx.vertex_v.x, ctx.vertex_w.x
            )
        )
    )
    b: TextureCoordinate = csfield(
        cs.Computed(
            lambda ctx: TextureCoordinate(
                ctx.vertex_u.y, ctx.vertex_v.y, ctx.vertex_w.y
            )
        )
    )
    c: TextureCoordinate = csfield(
        cs.Computed(
            lambda ctx: TextureCoordinate(
                ctx.vertex_u.z, ctx.vertex_v.z, ctx.vertex_w.z
            )
        )
    )


@dataclass
class Polygon(DataclassMixin):
    """Structure of polygon."""

    face: Face = csfield(DataclassStruct(Face))
    skip_optional_1E: bytes | None = csfield(cs.Optional(cs.Const(b"\x1E")))
    texture_mapping: TextureMapping = csfield(DataclassStruct(TextureMapping))
    skip_optional_1f: bytes | None = csfield(cs.Optional(cs.Const(b"\x1F")))
    normal: Vector3 | None = csfield(
        cs.If(lambda ctx: ctx.skip_optional_1f is not None, DataclassStruct(Vector3))
    )
    skip_optional_20: bytes | None = csfield(cs.Optional(cs.Const(b"\x20")))
    texture_index: int | None = csfield(
        cs.If(lambda ctx: ctx.skip_optional_20 is not None, cs.Byte)
    )
    skip_optional_1D: bytes | None = csfield(cs.Optional(cs.Const(b"\x1D")))


@dataclass
class AnimData(DataclassMixin):
    """Structure of anim data."""

    skip_required_38: bytes = csfield(cs.Const(b"\x38"))
    name: str = csfield(cs.CString("utf8"))
    skip_required_39: bytes = csfield(cs.Const(b"\x39"))
    x1: float = csfield(cs.Float32l)
    y1: float = csfield(cs.Float32l)
    z1: float = csfield(cs.Float32l)
    val: int = csfield(cs.Byte)
    x2: float = csfield(cs.Float32l)
    y2: float = csfield(cs.Float32l)
    z2: float = csfield(cs.Float32l)


@dataclass
class BgfModel(DataclassMixin):
    """Construct for BgfModel."""

    skip_required_19: bytes = csfield(cs.Const(b"\x19"))
    vertex_count: int = csfield(cs.Int16ul)
    skip_zero_2: bytes = csfield(cs.Const(b"\x00\x00"))
    skip_required_1A: bytes = csfield(cs.Const(b"\x1A"))
    polygon_count: int = csfield(cs.Int16ul)
    skip_zero_2_2: bytes = csfield(cs.Const(b"\x00\x00"))
    skip_required_1B: bytes = csfield(cs.Const(b"\x1B"))
    vertices: list[Vector3] = csfield(
        cs.Array(lambda ctx: ctx.vertex_count, DataclassStruct(Vector3))
    )
    skip_required_1C_1D: bytes = csfield(cs.Const(b"\x1C\x1D"))
    polygons: list[Polygon] = csfield(
        cs.Array(lambda ctx: ctx.polygon_count, DataclassStruct(Polygon))
    )


@dataclass
class BgfGameObject(DataclassMixin):
    """Construct for BgfGameObject."""

    skip_optional_28: bytes | None = csfield(cs.Optional(cs.Const(b"\x28")))
    skip_required_1415: bytes | None = csfield(cs.Const(b"\x14\x15"))
    name_bytes: bytes = csfield(cs.NullTerminated(cs.GreedyBytes))
    name: str = csfield(cs.Computed(lambda ctx: ctx.name_bytes.decode("latin-1")))
    skip_optional_1601: bytes | None = csfield(cs.Optional(cs.Const(b"\x16\x01")))
    padding_3: bytes | None = csfield(
        cs.If(
            lambda ctx: ctx.skip_optional_1601 is not None,
            cs.Padded(3, cs.Pass),
        )
    )
    skip_optional_1718: bytes | None = csfield(cs.Optional(cs.Const(b"\x17\x18")))
    padding_4: bytes | None = csfield(
        cs.If(
            lambda ctx: ctx.skip_optional_1718 is not None,
            cs.Padded(4, cs.Pass),
        )
    )
    model: BgfModel | None = csfield(
        cs.If(
            lambda ctx: ctx.skip_optional_1718 is not None,
            DataclassStruct(BgfModel),
        )
    )
    skip_optional_28_2: bytes | None = csfield(cs.Optional(cs.Const(b"\x28")))
    skip_optional_28_3: bytes | None = csfield(cs.Optional(cs.Const(b"\x28")))
    skip_optional_28_4: bytes | None = csfield(cs.Optional(cs.Const(b"\x28")))
    skip_optional_37: bytes | None = csfield(cs.Optional(cs.Const(b"\x37")))
    anim_count: int | None = csfield(
        cs.If(lambda ctx: ctx.skip_optional_37 is not None, cs.Int16ul)
    )
    padding_2: bytes | None = csfield(
        cs.If(
            lambda ctx: ctx.skip_optional_37 is not None,
            cs.Padded(2, cs.Pass),
        )
    )
    anim_data: list[AnimData] | None = csfield(
        cs.If(
            lambda ctx: ctx.skip_optional_37 is not None,
            cs.Array(lambda ctx: ctx.anim_count, DataclassStruct(AnimData)),
        )
    )


@dataclass
class VertexMapping(DataclassMixin):
    """Construct for VertexMapping."""

    vertex1: Vector3 = csfield(DataclassStruct(Vector3))
    vertex2: Vector3 = csfield(DataclassStruct(Vector3))


@dataclass
class PolygonMapping(DataclassMixin):
    """Construct for PolygonMapping."""

    face: Face = csfield(DataclassStruct(Face))
    texture_mapping: TextureMapping = csfield(DataclassStruct(TextureMapping))
    texture_index: int = csfield(cs.Byte)


@dataclass
class BgfMappingObject(DataclassMixin):
    """Construct for BgfMappingObject."""

    skip_required_2f_2d: bytes = csfield(cs.Const(b"\x2F\x2D"))
    num1: int = csfield(cs.Byte)
    num2: int = csfield(cs.Int16ul)
    padding_1: None = csfield(cs.Padded(1, cs.Pass))
    num3: int = csfield(cs.Int16ul)
    skip_required_b5_fa: bytes = csfield(cs.Const(b"\xB5\xFA"))
    texture_count: int = csfield(cs.Int32ul)
    vertex_mapping_count: int = csfield(cs.Int32ul)
    polygon_mapping_count: int = csfield(cs.Int32ul)
    vertex_mappings: list[VertexMapping] = csfield(
        cs.Array(lambda ctx: ctx.vertex_mapping_count, DataclassStruct(VertexMapping))
    )
    box_vertex_mappings: list[VertexMapping] = csfield(
        cs.Array(8, DataclassStruct(VertexMapping))
    )
    some_float: float = csfield(cs.Float32l)
    polygons: list[PolygonMapping] = csfield(
        cs.Array(lambda ctx: ctx.polygon_mapping_count, DataclassStruct(PolygonMapping))
    )


@dataclass
class BgfTexture(DataclassMixin):
    """Construct for BgfTexture."""

    skip_required_0506: bytes = csfield(cs.Const(b"\x05\x06"))
    id: int = csfield(cs.Int16ul)
    skip_zero_2: bytes = csfield(cs.Const(b"\x00\x00"))
    skip_optional_07: bytes | None = csfield(cs.Optional(cs.Const(b"\x07")))
    skip_optional_08: bytes | None = csfield(cs.Optional(cs.Const(b"\x08")))
    name_bytes: bytes = csfield(cs.NullTerminated(cs.GreedyBytes))
    name: str = ignoredcsfield(
        cs.Computed(lambda ctx: ctx.name_bytes.decode("latin-1"))
    )
    skip_optional_08_2: bytes | None = csfield(cs.Optional(cs.Const(b"\x08")))
    skip_optional_09: bytes | None = csfield(cs.Optional(cs.Const(b"\x09")))
    name_appendix: str | None = csfield(
        cs.If(
            lambda ctx: ctx.skip_optional_08_2 is not None
            or ctx.skip_optional_09 is not None,
            cs.CString("utf8"),
        )
    )
    const0A: bytes | None = csfield(cs.Optional(cs.Const(b"\x0A")))
    num0A: int | None = csfield(cs.If(lambda ctx: ctx.const0A is not None, cs.Byte))
    const0B: bytes | None = csfield(cs.Optional(cs.Const(b"\x0B")))
    num0B: int | None = csfield(cs.If(lambda ctx: ctx.const0B is not None, cs.Byte))
    # const0C: bytes = csfield(cs.Const(b"\x0C"))
    # num0C: int = csfield(cs.Byte)
    # const0D: bytes = csfield(cs.Const(b"\x0D"))
    # num0D: int = csfield(cs.Byte)
    # const0E: bytes = csfield(cs.Const(b"\x0E"))
    # num0E: int = csfield(cs.Byte)
    # const0F: bytes = csfield(cs.Const(b"\x0F"))
    # num0F: int = csfield(cs.Float32l)
    # const10: bytes = csfield(cs.Const(b"\x10"))
    # num10: int = csfield(cs.Float32l)
    # const11: bytes = csfield(cs.Const(b"\x11"))
    # num11: int = csfield(cs.Float32l)
    # const12: bytes = csfield(cs.Const(b"\x12"))
    # num12: int = csfield(cs.Float32l)
    # const13: bytes = csfield(cs.Const(b"\x13"))
    # num13: int = csfield(cs.Float32l)
    # skip bytes until 0x28
    skip_until_28: SkipUntil28 = csfield(DataclassStruct(SkipUntil28))

    @property
    def name_normalized(self) -> str:
        """Return the normalized name of the texture."""

        return Path(strip_non_ascii(self.name.lower())).stem


@dataclass
class BgfHeader(DataclassMixin):
    """Construct for BgfHeader."""

    name_bytes: bytes = csfield(cs.NullTerminated(cs.GreedyBytes))
    name: str = csfield(cs.Computed(lambda ctx: ctx.name_bytes.decode("latin-1")))
    skip_required_2e: bytes = csfield(cs.Const(b"\x2E"))
    mapping_address: int = csfield(cs.Int32ul)
    skip_required_0101: bytes = csfield(cs.Const(b"\x01\x01"))
    num1: int = csfield(cs.Int8ub)
    skip_required_cdab02: bytes = csfield(cs.Const(b"\xCD\xAB\x02"))
    num2: int = csfield(cs.Int8ub)
    skip_optional_37: bytes | None = csfield(cs.Optional(cs.Const(b"\x37")))
    anim_count: int | None = csfield(
        cs.If(
            lambda ctx: ctx.skip_optional_37 is not None,
            cs.Int16ul,
        )
    )
    skip_zero_2: bytes | None = csfield(
        cs.If(
            lambda ctx: ctx.skip_optional_37 is not None,
            cs.Const(b"\x00\x00"),
        )
    )
    skip_required_0304: bytes = csfield(cs.Const(b"\x03\x04"))
    texture_count: int = csfield(cs.Int16ul)
    skip_zero_2_2: bytes = csfield(cs.Const(b"\x00\x00"))


@dataclass
class BgfTextureName(DataclassMixin):
    """Construct for BgfTextureName."""

    name_bytes: bytes = csfield(cs.NullTerminated(cs.GreedyBytes))
    name: str = csfield(cs.Computed(lambda ctx: ctx.name_bytes.decode("latin-1")))
    skip_non_latin1: SkipNonLatin1 = csfield(DataclassStruct(SkipNonLatin1))
    optional_2f: bytes | None = csfield(cs.Optional(cs.Const(b"\x2F")))


@dataclass
class BgfFooter(DataclassMixin):
    """Construct for BgfFooter."""

    texture_names: list[BgfTextureName] = csfield(
        cs.GreedyRange(DataclassStruct(BgfTextureName))
    )

    # @staticmethod
    # def get_texture_names(textures: list[BgfTexture], footer_bytes: bytes) -> list[str]:
    #     """Extract texture names from footer bytes."""

    #     texture_names_to_position: dict[str, int] = {}

    #     for texture in textures:
    #         texture_full_name = texture.name
    #         texture_name = texture.name.split(".")[0]
    #         texture_name_bytes = texture_name.encode(OBJECTS_STRING_ENCODING)

    #         if texture_full_name in texture_names_to_position:
    #             continue

    #         position = footer_bytes.find(texture_name_bytes)

    #         if position == -1:
    #             continue

    #         texture_names_to_position[texture_full_name] = position

    #     texture_names = list(texture_names_to_position.keys())
    #     texture_names.sort(
    #         key=lambda texture_name: texture_names_to_position[texture_name]
    #     )

    #     return texture_names


@dataclass
class Bgf(BaseConstruct):
    """Construct for BGF files."""

    bgf_header: BgfHeader = csfield(DataclassStruct(BgfHeader))
    textures: list[BgfTexture] = csfield(cs.GreedyRange(DataclassStruct(BgfTexture)))
    game_objects: list[BgfGameObject] = csfield(
        cs.GreedyRange(DataclassStruct(BgfGameObject))
    )
    mapping_object: BgfMappingObject = csfield(DataclassStruct(BgfMappingObject))
    footer: BgfFooter = csfield(DataclassStruct(BgfFooter))

    @property
    def name(self) -> str:
        """Return the name of the construct."""

        return self.path.stem
