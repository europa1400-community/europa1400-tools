from dataclasses import dataclass

import construct as cs
from construct_typed import DataclassMixin, DataclassStruct, csfield

from europa_1400_tools.construct.base_construct import BaseConstruct


@dataclass
class RGB(DataclassMixin):
    """Structure of a RGB pixel."""

    red: int = csfield(cs.Byte)
    green: int = csfield(cs.Byte)
    blue: int = csfield(cs.Byte)


@dataclass
class RGBA(RGB):
    """Structure of a RGBA pixel."""

    alpha: int = csfield(cs.Byte)


@dataclass
class TransparencyBlock(DataclassMixin):
    """Structure of a transparency block."""

    size_transparent: int = csfield(cs.Int32ul)
    count_transparent: int = csfield(cs.Computed(lambda ctx: ctx.size_transparent // 3))
    count_pixels: int = csfield(cs.Int32ul)
    transparent_pixels: list[RGBA] = csfield(
        cs.Array(
            lambda ctx: ctx.count_transparent, cs.Computed(RGBA(0xFF, 0xFF, 0xFF, 0x00))
        )
    )
    pixels: list[RGB] = csfield(
        cs.Array(lambda ctx: ctx.count_pixels, DataclassStruct(RGB))
    )


@dataclass
class GraphicRow(DataclassMixin):
    """Structure of a graphic row."""

    block_count: int = csfield(cs.Int32ul)
    transparency_blocks: list[TransparencyBlock] = csfield(
        cs.Array(lambda ctx: ctx.block_count, DataclassStruct(TransparencyBlock))
    )


@dataclass
class Graphic(DataclassMixin):
    """Structure of a graphic."""

    size: int = csfield(cs.Int32ul)
    magic1: int = csfield(cs.Int16ul)
    width: int = csfield(cs.Int16ul)
    magic2: int = csfield(cs.Int16ul)
    height: int = csfield(cs.Int16ul)
    magic3: int = csfield(cs.Int16ul)
    magic4: int = csfield(cs.Int16ul)
    magic5: int = csfield(cs.Int16ul)
    width2: int = csfield(cs.Int16ul)
    height2: int = csfield(cs.Int16ul)
    magic6: int = csfield(cs.Int16ul)
    magic7: int = csfield(cs.Int16ul)
    magic8: int = csfield(cs.Int16ul)
    magic9: int = csfield(cs.Int16ul)
    magic10: int = csfield(cs.Int16ul)
    magic11: int = csfield(cs.Int16ul)
    magic12: int = csfield(cs.Int16ul)
    magic13: int = csfield(cs.Int16ul)
    magic14: int = csfield(cs.Int32ul)
    size_without_footer: int = csfield(cs.Int32ul)
    magic15: int = csfield(cs.Int32ul)
    footer_size: int = csfield(
        cs.Computed(lambda ctx: ctx.size - ctx.size_without_footer)
    )
    has_transparency: bool = csfield(
        cs.Computed(lambda ctx: ctx.size_without_footer > 0)
    )
    rgb_pixels: list[RGB] | None = csfield(
        cs.If(
            lambda ctx: not ctx.has_transparency,
            cs.Array(
                lambda ctx: ctx.height * ctx.width,
                DataclassStruct(RGB),
            ),
        )
    )
    graphic_rows: list[GraphicRow] | None = csfield(
        cs.If(
            lambda ctx: ctx.has_transparency,
            cs.Array(
                lambda ctx: ctx.height,
                DataclassStruct(GraphicRow),
            ),
        )
    )
    footer_data: list[int] | None = csfield(
        cs.If(
            lambda ctx: ctx.has_transparency,
            cs.Array(
                lambda ctx: ctx.footer_size // 4,
                cs.Int32ul,
            ),
        )
    )


@dataclass
class ShapebankDefinition(DataclassMixin):
    """Structure of a shapebank definition."""

    name: str = csfield(cs.PaddedString(48, "ascii"))
    address: int = csfield(cs.Int32ul)
    zeros1: bytes = csfield(cs.Bytes(4))
    size: int = csfield(cs.Int32ul)
    magic1: int = csfield(cs.Int32ul)
    zeros2: bytes = csfield(cs.Bytes(4))
    is_main_shapebank_int: int = csfield(cs.Byte)
    is_main_shapebank: bool = csfield(
        cs.Computed(lambda ctx: ctx.is_main_shapebank_int == 1)
    )
    zeros3: bytes = csfield(cs.Bytes(7))
    magic2: int = csfield(cs.Int32ul)
    width: int = csfield(cs.Int16ul)
    height: int = csfield(cs.Int16ul)


@dataclass
class Shapebank(DataclassMixin):
    """Structure of a shapebank."""

    const_shapbank: bytes = csfield(cs.Const(b"SHAPBANK"))
    magic1: int = csfield(cs.Byte)
    magic2: int = csfield(cs.Byte)
    zeros1: bytes = csfield(cs.Bytes(32))
    graphics_count: int = csfield(cs.Int16ul)
    magic_data1: list[int] = csfield(cs.Array(2, cs.Int16ul))
    size: int = csfield(cs.Int32ul)
    magic3: int = csfield(cs.Int32ul)
    zeros2: bytes = csfield(cs.Bytes(6))
    size_without_footer: int = csfield(cs.Int16ul)
    zeros3: bytes = csfield(cs.Bytes(3))
    magic4: int = csfield(cs.Int16ul)
    offsets: list[int] = csfield(
        cs.Padded(0x800, cs.Array(lambda ctx: ctx.graphics_count, cs.Int32ul))
    )
    graphics: list[Graphic] = csfield(
        cs.Array(lambda ctx: ctx.graphics_count, DataclassStruct(Graphic))
    )
    has_footer: bool = csfield(cs.Computed(lambda ctx: ctx.size_without_footer != 0))
    footer_size: int = csfield(
        cs.Computed(lambda ctx: ctx.graphics_count * 8 if ctx.has_footer else 0)
    )
    footer: bytes = csfield(cs.Bytes(lambda ctx: ctx.footer_size))


@dataclass
class Gfx(BaseConstruct):
    """Structure of the gfx file."""

    shapebank_count: int = csfield(cs.Int32ul)
    shapebank_definitions: list[ShapebankDefinition] = csfield(
        cs.Array(lambda ctx: ctx.shapebank_count, DataclassStruct(ShapebankDefinition))
    )
    main_shapebank_count: int = csfield(
        cs.Computed(
            lambda ctx: len(
                [
                    shapebank_definition
                    for shapebank_definition in ctx.shapebank_definitions
                    if shapebank_definition.is_main_shapebank
                ]
            )
        )
    )
    shapebanks: list[Shapebank] = csfield(
        cs.Array(lambda ctx: 197, DataclassStruct(Shapebank))
    )
