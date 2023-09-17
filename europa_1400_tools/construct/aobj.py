from dataclasses import dataclass

import construct as cs
from construct_typed import DataclassMixin, DataclassStruct, csfield

from europa_1400_tools.construct.base_construct import BaseConstruct


@dataclass
class Object(DataclassMixin):
    """Structure of object."""

    object_type: int = csfield(cs.Byte)
    name_bytes: bytes = csfield(cs.Bytes(32))
    name: str = csfield(
        cs.Computed(lambda ctx: ctx.name_bytes.decode("latin-1").rstrip("\x00"))
    )
    level: int = csfield(cs.Byte)
    time: int = csfield(cs.Int32ul)
    data1: list[int] = csfield(cs.Array(4, cs.Int16ul))
    data2: list[int] = csfield(cs.Array(4, cs.Int16ul))
    magic1: int = csfield(cs.Int16ul)
    price: int = csfield(cs.Int16ul)
    zeros1: bytes = csfield(cs.Bytes(2))
    magic2: int = csfield(cs.Int16ul)
    zeros2: bytes = csfield(cs.Bytes(2))
    magic3: int = csfield(cs.Byte)


@dataclass
class AObj(BaseConstruct):
    """Structure of A_Obj file."""

    objects: list[Object] = csfield(cs.Array(732, DataclassStruct(Object)))
