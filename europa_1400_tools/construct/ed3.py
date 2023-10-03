from dataclasses import dataclass

import construct as cs
from construct_typed import DataclassMixin, DataclassStruct, csfield

from europa_1400_tools.construct.base_construct import BaseConstruct
from europa_1400_tools.construct.common import Transform, Vector3, ignoredcsfield


def is_01(obj, ctx):
    return obj == 1


def cancel_on_unacceptable(obj, ctx):
    if obj not in ctx.acceptable_values:
        raise cs.CancelParsing


@dataclass
class Skip0(DataclassMixin):
    """Structure of a skip0 block."""

    acceptable_values: list[int] = ignoredcsfield(cs.Computed(lambda ctx: [0]))
    skipped: list[int] = ignoredcsfield(
        cs.GreedyRange(cs.Byte * cancel_on_unacceptable)
    )


@dataclass
class Skip01(DataclassMixin):
    """Structure of a skip01 block."""

    acceptable_values: list[int] = ignoredcsfield(cs.Computed(lambda ctx: [0, 1]))
    skipped: list[int] = ignoredcsfield(
        cs.GreedyRange(cs.Byte * cancel_on_unacceptable)
    )


@dataclass
class Skip1(DataclassMixin):
    """Structure of a skip01 block."""

    acceptable_values: list[int] = ignoredcsfield(cs.Computed(lambda ctx: [1]))
    skipped: list[int] = ignoredcsfield(
        cs.GreedyRange(cs.Byte * cancel_on_unacceptable)
    )


@dataclass
class MainCameraElementAf(DataclassMixin):
    """Structure of a camera element."""

    name: str = csfield(cs.CString("ascii"))
    values: list[float] = csfield(cs.Array(22, cs.Float32l))
    maincameraaf_num1: int = csfield(cs.Int32ul)
    skip0: Skip0 = ignoredcsfield(DataclassStruct(Skip0))


@dataclass
class MainCameraNums(DataclassMixin):
    """Structure of a main camera elements nums."""

    maincameranums_num1: int = csfield(cs.Byte)
    maincameranums_num2: int = csfield(cs.Byte)
    maincameranums_num3: int = csfield(cs.Byte)
    maincameranums_num4: int = csfield(cs.Byte)


@dataclass
class CameraData(DataclassMixin):
    """Structure of a camera data."""

    values1: list[float] = csfield(cs.Array(17, cs.Float32l))
    nums1: MainCameraNums = csfield(DataclassStruct(MainCameraNums))
    values2: list[float] = csfield(cs.Array(2, cs.Float32l))
    nums2: MainCameraNums = csfield(DataclassStruct(MainCameraNums))
    values3: list[float] = csfield(cs.Array(2, cs.Float32l))
    nums3: MainCameraNums = csfield(DataclassStruct(MainCameraNums))


@dataclass
class MainCameraElement(DataclassMixin):
    """Structure of a camera element."""

    name: str = csfield(cs.CString("ascii"))
    camera_data_count: int = csfield(
        cs.Computed(lambda ctx: 5 if ctx._.type == 0xB9 else 6)
    )
    values1: list[float] = csfield(cs.Array(7, cs.Float32l))
    maincameraelement_num1: int = csfield(cs.Byte)
    maincameraelement_num2: int = csfield(cs.Byte)
    maincameraelement_num3: int = csfield(cs.Byte)
    maincameraelement_num4: int = csfield(cs.Byte)
    nums1: MainCameraNums = csfield(DataclassStruct(MainCameraNums))
    values2: list[float] = csfield(cs.Array(8, cs.Float32l))
    nums2: MainCameraNums = csfield(DataclassStruct(MainCameraNums))
    values3: list[float] = csfield(cs.Array(2, cs.Float32l))
    nums3: MainCameraNums = csfield(DataclassStruct(MainCameraNums))
    values4: list[float] = csfield(cs.Array(2, cs.Float32l))
    nums4: MainCameraNums = csfield(DataclassStruct(MainCameraNums))
    camera_datas: list[CameraData] = csfield(
        cs.Array(lambda ctx: ctx.camera_data_count, DataclassStruct(CameraData))
    )
    values5: list[float] = csfield(cs.Array(11, cs.Float32l))
    num5: int = csfield(cs.Byte)
    skip0: Skip0 = ignoredcsfield(DataclassStruct(Skip0))


@dataclass
class CityFooter(DataclassMixin):
    """Structure of a city footer."""

    names: list[str] = csfield(cs.Array(8, cs.CString("ascii")))
    values: list[float] = csfield(cs.Array(5, cs.Float32l))


@dataclass
class WaterData(DataclassMixin):
    """Structure of a water data."""

    name: str = csfield(cs.CString("ascii"))
    zero1: bytes = ignoredcsfield(cs.Bytes(3))
    waterdata_num1: int = csfield(cs.Int32ul)
    values: list[float] = csfield(cs.Array(11, cs.Float32l))
    waterdata_num2: int = csfield(cs.Int32ul)


@dataclass
class WaterElement(DataclassMixin):
    """Structure of a water element."""

    water_data_count: int = csfield(cs.Int32ul)
    width: int = csfield(cs.Int32ul)
    height: int = csfield(cs.Int32ul)
    data: list[int] = csfield(cs.Array(lambda ctx: ctx._.size, cs.Byte))
    water_datas: list[WaterData] = csfield(
        cs.Array(lambda ctx: ctx.water_data_count, DataclassStruct(WaterData)),
    )


@dataclass
class TextureElement(DataclassMixin):
    """Structure of a texture element."""

    name: str = csfield(cs.CString("ascii"))
    width: int = csfield(cs.Int32ul)
    height: int = csfield(cs.Int32ul)
    values: list[int] = csfield(cs.Array(lambda ctx: ctx._.size, cs.Byte))


@dataclass
class CityElement(DataclassMixin):
    """Structure of a city element."""

    size: int = csfield(cs.Computed(lambda ctx: ctx._.width * ctx._.height))
    height_data1: list[int] = csfield(cs.Array(lambda ctx: ctx.size, cs.Byte))
    cityelement_num1: int = csfield(cs.Int32ul)
    zero1: bytes = ignoredcsfield(cs.Bytes(1))
    cityelement_num2: int = csfield(cs.Byte)
    flag1: bool = csfield(cs.Flag)
    height_data2: list[int] = csfield(cs.Array(lambda ctx: ctx.size * 4, cs.Byte))
    zero2: bytes = ignoredcsfield(cs.Bytes(1))
    has_water_element: bool = csfield(cs.Flag)
    water_element: WaterElement | None = csfield(
        cs.If(lambda ctx: ctx.has_water_element, DataclassStruct(WaterElement))
    )
    texture_element: TextureElement = csfield(DataclassStruct(TextureElement))
    footer: CityFooter = csfield(DataclassStruct(CityFooter))


@dataclass
class ContactElement(DataclassMixin):
    """Structure of a dummy0 element."""

    flag1: bool = csfield(cs.Flag)
    flag2: bool = csfield(cs.Flag)
    vectors: list[Vector3] = csfield(cs.Array(3, DataclassStruct(Vector3)))
    value: float = csfield(cs.Float32l)


@dataclass
class DummyElement(DataclassMixin):
    """Structure of a dummy element."""

    flag1: bool = csfield(cs.Flag)
    transform: Transform = csfield(DataclassStruct(Transform))
    flag2: bool = csfield(cs.Flag)
    transforms: list[Transform] = csfield(cs.Array(7, DataclassStruct(Transform)))


@dataclass
class CameraElement(DataclassMixin):
    """Structure of a camera element."""

    flag1: bool = csfield(cs.Flag)
    transform: Transform = csfield(DataclassStruct(Transform))
    flag2: bool = csfield(cs.Flag)
    transforms: list[Transform] = csfield(cs.Array(11, DataclassStruct(Transform)))


@dataclass
class ObjectElement(DataclassMixin):
    """Structure of an object element."""

    flag1: bool = csfield(cs.Flag)
    zero1: bytes = ignoredcsfield(cs.Bytes(1))
    flag2: bool = csfield(cs.Flag)
    flag3: bool = csfield(cs.Flag)
    objectelement_num1: int = csfield(cs.Byte)
    flag4: bool = csfield(cs.Flag)
    flag5: bool | None = csfield(
        cs.If(
            lambda ctx: ctx._._._.type != 0xAF,
            cs.Flag,
        )
    )
    flag6: bool | None = csfield(
        cs.If(
            lambda ctx: ctx._._._.type != 0xAF,
            cs.Flag,
        )
    )
    objectelement_num2: int = csfield(cs.Byte)
    zero2: bytes = ignoredcsfield(cs.Bytes(1))
    flag7: bool = csfield(cs.Flag)
    zero3: bytes = ignoredcsfield(cs.Bytes(1))
    has_object_name: bool = ignoredcsfield(cs.Flag)
    zero4: bytes = ignoredcsfield(cs.Bytes(3))
    name: str | None = csfield(
        cs.If(lambda ctx: ctx.has_object_name, cs.CString("ascii"))
    )
    transform: Transform = csfield(DataclassStruct(Transform))
    flag8: bool = csfield(cs.Flag)
    transforms: list[Transform] = csfield(cs.Array(6, DataclassStruct(Transform)))


@dataclass
class LightBlock(DataclassMixin):
    """Structure of a light block."""

    values: list[float] = csfield(cs.Array(13, cs.Float32l))
    num: int = csfield(cs.Int32ul)


@dataclass
class LightElement(DataclassMixin):
    """Structure of a light element."""

    block_count: int = ignoredcsfield(
        cs.Computed(
            lambda ctx: 7 if ctx._._._.type == 0xB9 or ctx._._._.type == 0xAF else 8
        )
    )
    flag1: bool = csfield(cs.Flag)
    flag2: bool = csfield(cs.Flag)
    is_not_r_light: bool = csfield(cs.Flag)
    blocks: list[LightBlock] = csfield(
        cs.Array(lambda ctx: ctx.block_count, DataclassStruct(LightBlock)),
    )


@dataclass
class Script(DataclassMixin):
    """Structure of a script."""

    event_name: str = csfield(cs.CString("ascii"))
    script_path: str = csfield(cs.CString("ascii"))


@dataclass
class ScriptElement(DataclassMixin):
    """Structure of a script element."""

    script_count: int = ignoredcsfield(cs.Int32ul)
    scripts: list[Script] = csfield(
        cs.Array(lambda ctx: ctx.script_count, DataclassStruct(Script))
    )
    skip0: Skip0 = ignoredcsfield(DataclassStruct(Skip0))


@dataclass
class SceneElement(DataclassMixin):
    """Structure of a scene element."""

    skip1: Skip1 = ignoredcsfield(DataclassStruct(Skip1))
    name: str = csfield(cs.CString("ascii"))
    width: int = csfield(cs.Int32ul)
    height: int | None = csfield(cs.If(lambda ctx: ctx._._.type != 0xAF, cs.Int32ul))
    type: int = csfield(cs.Int32ul)
    city_element: CityElement | None = csfield(
        cs.If(
            lambda ctx: ctx.width == 0x40 or ctx.width == 0x80 or ctx.width == 0x100,
            DataclassStruct(CityElement),
        )
    )
    contact_element: ContactElement | None = csfield(
        cs.If(
            lambda ctx: ctx.type == 0x00,
            DataclassStruct(ContactElement),
        )
    )
    dummy_element: DummyElement | None = csfield(
        cs.If(
            lambda ctx: ctx.type == 0x02,
            DataclassStruct(DummyElement),
        )
    )
    camera_element: CameraElement | None = csfield(
        cs.If(
            lambda ctx: ctx.type == 0x03,
            DataclassStruct(CameraElement),
        )
    )
    object_element: ObjectElement | None = csfield(
        cs.If(
            lambda ctx: ctx.type == 0x04,
            DataclassStruct(ObjectElement),
        )
    )
    light_element: LightElement | None = csfield(
        cs.If(
            lambda ctx: ctx.type == 0x05
            or ctx.type == 0x06
            or ctx.type == 0x07
            or ctx.type == 0x08,
            DataclassStruct(LightElement),
        )
    )
    skip0: Skip0 = ignoredcsfield(DataclassStruct(Skip0))
    script_elements: list[ScriptElement] = csfield(
        cs.GreedyRange(DataclassStruct(ScriptElement))
    )


def is_sub_element(obj: SceneElement, ctx):
    if obj.skip1.skipped != [1, 1]:
        raise cs.CancelParsing


@dataclass
class ElementGroup(DataclassMixin):
    """Structure of an element group."""

    skip1: Skip1 = ignoredcsfield(DataclassStruct(Skip1))
    first_element: SceneElement = csfield(DataclassStruct(SceneElement))
    elements: list[SceneElement] = csfield(
        cs.GreedyRange(DataclassStruct(SceneElement) * is_sub_element)
    )


def is_element_group(obj, ctx):
    if obj.skip1.skipped != [1]:
        raise cs.CancelParsing


@dataclass
class Ed3(BaseConstruct):
    """Structure of an ed3 file."""

    type: int = csfield(cs.Byte)
    const: bytes = ignoredcsfield(cs.Const(b"\x00\x6c\x3a"))
    main_camera_element: MainCameraElement = csfield(DataclassStruct(MainCameraElement))
    element_groups: list[ElementGroup] = csfield(
        cs.GreedyRange(DataclassStruct(ElementGroup) * is_element_group)
    )
