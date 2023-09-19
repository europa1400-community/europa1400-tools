from dataclasses import dataclass

import construct as cs
from construct_typed import DataclassMixin, DataclassStruct, csfield


@dataclass
class Vector3(DataclassMixin):
    x: float = csfield(cs.Float32l)
    y: float = csfield(cs.Float32l)
    z: float = csfield(cs.Float32l)


@dataclass
class Transform(DataclassMixin):
    """Structure of a transform block."""

    position: Vector3 = csfield(DataclassStruct(Vector3))
    rotation: Vector3 = csfield(DataclassStruct(Vector3))
