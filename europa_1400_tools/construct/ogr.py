"""Construct for OGR files."""

from dataclasses import dataclass

import construct as cs
from construct_typed import DataclassMixin, DataclassStruct, csfield

from europa_1400_tools.const import Format, SourceFormat
from europa_1400_tools.construct.baf import Vertex
from europa_1400_tools.construct.base_construct import BaseConstruct


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
class Skip013(DataclassMixin):
    """Structure of a skip013 block."""

    acceptable_values: list[int] = csfield(cs.Computed(lambda ctx: [0, 1, 3]))
    skipped: list[int] = csfield(cs.GreedyRange(cs.Byte * cancel_on_unacceptable))


@dataclass
class Skip12345678(DataclassMixin):
    """Structure of a skip0123456 block."""

    acceptable_values: list[int] = csfield(
        cs.Computed(lambda ctx: [1, 2, 3, 4, 5, 6, 7, 8])
    )
    skipped: list[int] = csfield(cs.GreedyRange(cs.Byte * cancel_on_unacceptable))


@dataclass
class Skip012345678(DataclassMixin):
    """Structure of a skip0123456 block."""

    acceptable_values: list[int] = csfield(
        cs.Computed(lambda ctx: [0, 1, 2, 3, 4, 5, 6, 7, 8])
    )
    skipped: list[int] = csfield(cs.GreedyRange(cs.Byte * cancel_on_unacceptable))


@dataclass
class LightDataBlock(DataclassMixin):
    """Structure of a light data block."""

    data: list[float] = csfield(cs.Array(9, cs.Float32l))
    zeros: bytes = csfield(cs.Bytes(12))
    skipped: bytes | None = csfield(
        cs.If(
            lambda ctx: ctx._.data_padding > 0, cs.Bytes(lambda ctx: ctx._.data_padding)
        )
    )


@dataclass
class ObjectData(DataclassMixin):
    """Structure of a object data block."""

    offset: Vertex = csfield(DataclassStruct(Vertex))
    data: Vertex = csfield(DataclassStruct(Vertex))


@dataclass
class DummyElement(DataclassMixin):
    """Structure of a dummy element."""

    skipped: bytes = csfield(cs.Bytes(4))
    object_data: ObjectData = csfield(DataclassStruct(ObjectData))


@dataclass
class ObjectElement(DataclassMixin):
    """Structure of a object element."""

    skip0123456: Skip012345678 = csfield(DataclassStruct(Skip012345678))
    name: str = csfield(cs.CString("ascii"))
    object_data: ObjectData = csfield(DataclassStruct(ObjectData))
    additional_flag: int | None = csfield(
        cs.If(lambda ctx: cs.Peek(cs.Byte) == 1, cs.Byte)
    )
    object_data_additional: ObjectData | None = csfield(
        cs.If(lambda ctx: ctx.additional_flag == 1, DataclassStruct(ObjectData))
    )


@dataclass
class LightElement(DataclassMixin):
    """Structure of a footer element."""

    skipped: bytes = csfield(cs.Bytes(6))
    data_padding: int = csfield(cs.Computed(lambda ctx: len(ctx._.skip013.skipped)))
    data_count: int = csfield(
        cs.Computed(
            lambda ctx: 8
            if ctx.footer_padding == 8 and ctx._.type != 7 and ctx._.type != 8
            else 7
        )
    )
    light_data_blocks: list[LightDataBlock] = csfield(
        cs.Array(lambda ctx: ctx.data_count, DataclassStruct(LightDataBlock))
    )


@dataclass
class GroupElement(DataclassMixin):
    """Structure of a group element."""

    skip01: Skip01 = csfield(DataclassStruct(Skip01))
    name: str = csfield(cs.CString("ascii"))
    skip013: Skip013 = csfield(DataclassStruct(Skip013))
    type: int = csfield(cs.Byte)
    dummy_element: DummyElement | None = csfield(
        cs.If(lambda ctx: ctx.type == 2, DataclassStruct(DummyElement))
    )
    object_element: ObjectElement | None = csfield(
        cs.If(lambda ctx: ctx.type == 4, DataclassStruct(ObjectElement))
    )
    light_element: LightElement | None = csfield(
        cs.If(
            lambda ctx: ctx.type == 5
            or ctx.type == 6
            or ctx.type == 7
            or ctx.type == 8,
            DataclassStruct(LightElement),
        )
    )


@dataclass
class Ogr(BaseConstruct):
    """Structure of a OGR file."""

    magic1: int = csfield(cs.Byte)
    magic2: int = csfield(cs.Byte)
    magic3: int = csfield(cs.Int16ul)
    skipped1: bytes = csfield(DataclassStruct(Skip12345678))
    skipped2: bytes = csfield(DataclassStruct(Skip0))

    group_elements: list[GroupElement] = csfield(
        cs.GreedyRange(DataclassStruct(GroupElement) * is_01)
    )

    @property
    def format(self) -> SourceFormat:
        return SourceFormat.OGR

    @property
    def ignored_fields(self) -> list[str]:
        """Return the list of ignored fields."""

        return [
            "skipped",
            "skipped1",
            "skipped2",
            "skip01",
            "skip013",
            "skip0123456",
            "padding",
            "padding1",
            "padding2",
            "padding3",
            "const_1e",
            "skip0",
            "type1",
            "type2",
            "type3",
            "zeros",
            "data_padding",
        ]
