"""Construct structures for A_Geb file."""

from dataclasses import dataclass

import construct as cs
from construct_typed import DataclassMixin, DataclassStruct, csfield

from europa_1400_tools.construct.base_construct import BaseConstruct


@dataclass
class Point(DataclassMixin):
    """Structure of point."""

    a: int = csfield(cs.Byte)
    b: int = csfield(cs.Byte)
    c: int = csfield(cs.Byte)


@dataclass
class Building(DataclassMixin):
    """Structure of building."""

    building_group_id: int = csfield(cs.Byte)
    name: str = csfield(cs.PaddedString(32, "ascii"))
    magic_byte: int = csfield(cs.Byte)
    size_data: int = csfield(cs.Byte)
    data1: list[int] = csfield(cs.Padded(136, cs.Array(cs.this.size_data, cs.Int16ul)))
    data2: list[int] = csfield(cs.Padded(248, cs.Array(cs.this.size_data, cs.Int32ul)))
    data3: list[int] = csfield(cs.Padded(65, cs.Array(cs.this.size_data, cs.Byte)))
    data4: list[int] = csfield(cs.Padded(63, cs.Array(cs.this.size_data, cs.Byte)))
    data5: list[int] = csfield(cs.Array(26, cs.Byte))
    point1: Point = csfield(DataclassStruct(Point))
    point2: Point = csfield(DataclassStruct(Point))
    time: int = csfield(cs.Int32ul)
    level: int = csfield(cs.Byte)
    magic_byte2: int = csfield(cs.Byte)
    price: int = csfield(cs.Int32ul)


@dataclass
class AGeb(BaseConstruct):
    """Structure of A_Geb file."""

    buildings: list[Building] = csfield(cs.Array(88, DataclassStruct(Building)))
