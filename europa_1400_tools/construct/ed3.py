from dataclasses import dataclass

import construct as cs
from construct_typed import DataclassMixin, DataclassStruct, csfield

from europa_1400_tools.construct.baf import Vector3
from europa_1400_tools.construct.base_construct import BaseConstruct
from europa_1400_tools.construct.common import Transform


def is_01(obj, ctx):
    return obj == 1


def cancel_on_unacceptable(obj, ctx):
    if obj not in ctx.acceptable_values:
        raise cs.CancelParsing


@dataclass
class Skip0(DataclassMixin):
    """Structure of a skip0 block."""

    acceptable_values: list[int] = csfield(cs.Computed(lambda ctx: [0]))
    skipped: list[int] = csfield(cs.GreedyRange(cs.Byte * cancel_on_unacceptable))


@dataclass
class Skip01(DataclassMixin):
    """Structure of a skip01 block."""

    acceptable_values: list[int] = csfield(cs.Computed(lambda ctx: [0, 1]))
    skipped: list[int] = csfield(cs.GreedyRange(cs.Byte * cancel_on_unacceptable))


@dataclass
class MainCameraElement(DataclassMixin):
    """Structure of a camera element."""

    name: str = csfield(cs.CString("ascii"))
    nums: float = csfield(cs.Array(179, cs.Float32l))
    magic: int = csfield(cs.Byte)
    skipped: bytes = csfield(cs.Bytes(24))


@dataclass
class WaterBlock(DataclassMixin):
    """Structure of a water block."""

    padding: bytes = csfield(cs.Bytes(3))
    type: int = csfield(cs.Byte)
    padding2: bytes = csfield(cs.Bytes(3))
    data: list[float] = csfield(cs.Array(11, cs.Float32l))
    num: int = csfield(cs.Int32ul)


@dataclass
class TextureBlock(DataclassMixin):
    """Structure of a texture block."""

    padding: bytes = csfield(cs.Bytes(8))
    data: list[int] = csfield(cs.Bytes(lambda ctx: ctx._._.size))


@dataclass
class CityBlock(DataclassMixin):
    """Structure of a city block."""

    name: str = csfield(cs.CString("ascii"))

    water_flag: int = csfield(cs.Peek(cs.Bytes(4)))
    texture_flag: int = csfield(cs.Peek(cs.Bytes(5)))
    water_block: WaterBlock | None = csfield(
        cs.If(
            lambda ctx: ctx.water_flag == b"\x00\x00\x00\xDC"
            or ctx.water_flag == b"\x00\x00\x00\xC8"
            or ctx.water_flag == b"\x00\x00\x00\xCD"
            or ctx.water_flag == b"\x00\x00\x00\xE6",
            DataclassStruct(WaterBlock),
        )
    )
    texture_block: TextureBlock | None = csfield(
        cs.If(
            lambda ctx: ctx.texture_flag == b"\x80\x00\x00\x00\x80"
            or ctx.texture_flag == b"\x40\x00\x00\x00\x40",
            DataclassStruct(TextureBlock),
        )
    )


@dataclass
class CityFooter(DataclassMixin):
    """Structure of a city footer."""

    names: list[str] = csfield(cs.GreedyRange(cs.CString("ascii")))
    data: bytes = csfield(cs.GreedyBytes)


@dataclass
class CityElement(DataclassMixin):
    """Structure of a city element."""

    padding1: bytes = csfield(cs.Bytes(3))
    size: int = csfield(cs.Computed(lambda ctx: ctx._.type1 * ctx._.type2))
    height_data1: list[int] = csfield(cs.Bytes(lambda ctx: ctx.size))
    magic: int = csfield(cs.Int32ul)
    padding2: bytes = csfield(cs.Bytes(1))
    magic2: int = csfield(cs.Byte)
    padding3: bytes = csfield(cs.Bytes(2))
    height_data2: list[int] = csfield(cs.Bytes(lambda ctx: ctx.size * 4))
    height_data3_flag: int = csfield(cs.Peek(cs.Byte))
    magic3: int | None = csfield(cs.Optional(cs.Const(b"\x02\x00\x00\x00")))
    a: int | None = csfield(
        cs.If(
            lambda ctx: ctx.height_data3_flag == 0x01,
            cs.Int32ul,
        )
    )
    b: int | None = csfield(
        cs.If(
            lambda ctx: ctx.height_data3_flag == 0x01,
            cs.Int32ul,
        )
    )
    height_data3: list[int] | None = csfield(
        cs.If(
            lambda ctx: ctx.height_data3_flag == 0x01,
            cs.Bytes(lambda ctx: ctx.size),
        )
    )
    skip0: Skip0 = csfield(DataclassStruct(Skip0))
    const_1e: int | None = csfield(cs.Optional(cs.Const(b"\x1e")))
    blocks: list[CityBlock] = csfield(
        cs.GreedyRange(DataclassStruct(CityBlock)),
    )
    footer: CityFooter = csfield(DataclassStruct(CityFooter))


@dataclass
class DummyElement0(DataclassMixin):
    """Structure of a dummy0 element."""

    padding: bytes = csfield(cs.Bytes(5))
    data: list[float] = csfield(cs.Array(10, cs.Float32l))


@dataclass
class DummyElement(DataclassMixin):
    """Structure of a dummy element."""

    padding: bytes = csfield(cs.Bytes(4))
    transform: Transform = csfield(DataclassStruct(Transform))
    padding2: bytes = csfield(cs.Bytes(1))
    transforms: list[Transform] = csfield(cs.Array(10, DataclassStruct(Transform)))


@dataclass
class CameraElement(DataclassMixin):
    """Structure of a camera element."""

    padding: bytes = csfield(cs.Bytes(4))
    transform: Transform = csfield(DataclassStruct(Transform))
    padding2: bytes = csfield(cs.Bytes(1))
    transforms: list[Transform] = csfield(cs.Array(11, DataclassStruct(Transform)))


@dataclass
class ObjectElement(DataclassMixin):
    """Structure of an object element."""

    padding: bytes = csfield(cs.Bytes(19))
    name: str = csfield(cs.CString("ascii"))
    transforms: Transform = csfield(cs.Array(11, DataclassStruct(Transform)))


@dataclass
class LightBlock(DataclassMixin):
    """Structure of a light block."""

    data: list[float] = csfield(cs.Array(13, cs.Float32l))
    skipped: int = csfield(cs.Bytes(4))


@dataclass
class LightElement(DataclassMixin):
    """Structure of a light element."""

    padding: bytes = csfield(cs.Bytes(6))
    blocks: list[LightBlock] = csfield(
        cs.Array(8, DataclassStruct(LightBlock)),
    )


@dataclass
class SceneElement(DataclassMixin):
    """Structure of a scene element."""

    skip01: Skip01 = csfield(DataclassStruct(Skip01))
    name: str = csfield(cs.CString("ascii"))
    type1: int = csfield(cs.Int32ul)
    type2: int = csfield(cs.Int32ul)
    type3: int = csfield(cs.Byte)
    city_element: CityElement | None = csfield(
        cs.If(
            lambda ctx: ctx.type1 == 0x80 or ctx.type1 == 0x40,
            DataclassStruct(CityElement),
        )
    )
    dummy0_element: DummyElement0 | None = csfield(
        cs.If(
            lambda ctx: ctx.type1 != 0x80 and ctx.type1 != 0x40 and ctx.type3 == 0x00,
            DataclassStruct(DummyElement0),
        )
    )
    dummy_element: DummyElement | None = csfield(
        cs.If(
            lambda ctx: ctx.type1 != 0x80 and ctx.type1 != 0x40 and ctx.type3 == 0x02,
            DataclassStruct(DummyElement),
        )
    )
    camera_element: CameraElement | None = csfield(
        cs.If(
            lambda ctx: ctx.type1 != 0x80 and ctx.type1 != 0x40 and ctx.type3 == 0x03,
            DataclassStruct(CameraElement),
        )
    )
    object_element: ObjectElement | None = csfield(
        cs.If(
            lambda ctx: ctx.type1 != 0x80 and ctx.type1 != 0x40 and ctx.type3 == 0x04,
            DataclassStruct(ObjectElement),
        )
    )
    light_element5: LightElement | None = csfield(
        cs.If(
            lambda ctx: ctx.type1 != 0x80 and ctx.type1 != 0x40 and ctx.type3 == 0x05,
            DataclassStruct(LightElement),
        )
    )
    light_element7: LightElement | None = csfield(
        cs.If(
            lambda ctx: ctx.type1 != 0x80 and ctx.type1 != 0x40 and ctx.type3 == 0x07,
            DataclassStruct(LightElement),
        )
    )
    light_element8: LightElement | None = csfield(
        cs.If(
            lambda ctx: ctx.type1 != 0x80 and ctx.type1 != 0x40 and ctx.type3 == 0x08,
            DataclassStruct(LightElement),
        )
    )
    skip0: Skip0 = csfield(DataclassStruct(Skip0))


def is_sub_element(obj: SceneElement, ctx):
    if obj.skip01.skipped != [1, 1]:
        raise cs.CancelParsing


@dataclass
class ElementGroup(DataclassMixin):
    """Structure of an element group."""

    skip01: Skip01 = csfield(DataclassStruct(Skip01))
    first_element: SceneElement = csfield(DataclassStruct(SceneElement))
    elements: list[SceneElement] = csfield(
        cs.GreedyRange(DataclassStruct(SceneElement) * is_sub_element)
    )


def is_element_group(obj: ElementGroup, ctx):
    if obj.skip01.skipped != [1]:
        raise cs.CancelParsing


@dataclass
class Ed3(BaseConstruct):
    """Structure of an ed3 file."""

    skipped: bytes = csfield(cs.Bytes(4))
    main_camera_element: MainCameraElement = csfield(DataclassStruct(MainCameraElement))
    element_groups: list[ElementGroup] = csfield(
        cs.GreedyRange(DataclassStruct(ElementGroup) * is_element_group)
    )

    @property
    def ignored_fields(self) -> list[str]:
        """Return the list of ignored fields."""

        return [
            "skipped",
            "skip01",
            "padding",
            "padding1",
            "padding2",
            "padding3",
            "const_1e",
            "skip0",
            "type1" "type2" "type3",
        ]
