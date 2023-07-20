import configparser
from dataclasses import dataclass
from pathlib import Path

import construct as cs
import numpy as np
from construct_typed import DataclassMixin, DataclassStruct, csfield

from europa_1400_tools.const import (
    BAF_INI_FILE_KEYS,
    BAF_INI_FILE_LOOP_IN,
    BAF_INI_FILE_LOOP_OUT,
    BAF_INI_FILE_NUM_KEYS,
    BAF_INI_FILE_SECTION,
    SourceFormat,
)
from europa_1400_tools.construct.base_construct import BaseConstruct


@dataclass
class Vertex(DataclassMixin):
    x: float = csfield(cs.Float32l)
    y: float = csfield(cs.Float32l)
    z: float = csfield(cs.Float32l)


@dataclass
class AnimHeader(DataclassMixin):
    magic: bytes = csfield(cs.Const(b"\x42\x47\x46\0"))
    const_30: bytes = csfield(cs.Const(b"\x30"))
    fsize_less_10: int = csfield(cs.Int32ul)
    const_01: bytes = csfield(cs.Const(b"\x01"))
    a: int = csfield(cs.Int16ul)
    const_cdab23: bytes = csfield(cs.Const(b"\xCD\xAB\x23"))
    num_keys: int = csfield(cs.Int32ul)
    const_3301: bytes | None = csfield(cs.Optional(cs.Const(b"\x33\x01")))
    const_2400: bytes | None = csfield(cs.Optional(cs.Const(b"\x24\x00")))
    const_37: bytes | None = csfield(cs.Optional(cs.Const(b"\x37")))
    b: int | None = csfield(cs.If(lambda ctx: ctx.const_37, cs.Int32ul))
    const_36: bytes | None = csfield(cs.Optional(cs.Const(b"\x36")))
    optional_groups_per_key: int | None = csfield(
        cs.If(lambda ctx: ctx.const_36, cs.Int32ul)
    )
    groups_per_key: int = csfield(
        cs.Computed(
            lambda ctx: ctx.optional_groups_per_key
            if ctx.optional_groups_per_key
            else 1
        )
    )
    const_34: bytes | None = csfield(cs.Optional(cs.Const(b"\x34")))
    num_points: int | None = csfield(cs.If(lambda ctx: ctx.const_34, cs.Int32ul))
    d_flag: bytes | None = csfield(cs.Optional(cs.Const(b"\x29")))
    d: int | None = csfield(cs.If(lambda ctx: ctx.d_flag, cs.Int32ul))
    e_flag: bytes | None = csfield(cs.Optional(cs.Const(b"\x2A")))
    e: int | None = csfield(cs.If(lambda ctx: ctx.e_flag, cs.Int32ul))


@dataclass
class SkeletonData(DataclassMixin):
    point_a: Vertex = csfield(DataclassStruct(Vertex))
    const_3A: bytes = csfield(cs.Const(b"\x3A"))
    point_b: Vertex = csfield(DataclassStruct(Vertex))


@dataclass
class Skeleton(DataclassMixin):
    const_38: bytes | None = csfield(cs.Optional(cs.Const(b"\x38")))
    name: str | None = csfield(cs.If(lambda ctx: ctx.const_38, cs.CString("ascii")))
    data_flag: bytes | None = csfield(cs.Optional(cs.Const(b"\x39")))
    data: SkeletonData | None = csfield(
        cs.If(
            lambda ctx: ctx.data_flag,
            DataclassStruct(SkeletonData),
        )
    )


@dataclass
class SkeletonContainer(DataclassMixin):
    point_a: Vertex = csfield(DataclassStruct(Vertex))
    point_b: Vertex = csfield(DataclassStruct(Vertex))

    skeleton_head: Skeleton = csfield(DataclassStruct(Skeleton))
    skeleton_left_hand: Skeleton = csfield(DataclassStruct(Skeleton))
    skeleton_right_hand: Skeleton = csfield(DataclassStruct(Skeleton))


@dataclass
class PointContainer(DataclassMixin):
    const_18: bytes = csfield(cs.Const(b"\x18"))
    id: int = csfield(cs.Int32ul)
    const_19: bytes = csfield(cs.Const(b"\x19"))
    count: int = csfield(cs.Int32ul)
    const_21: bytes = csfield(cs.Const(b"\x21"))
    vertices: list[Vertex] = csfield(cs.Array(cs.this.count, DataclassStruct(Vertex)))
    const_28: bytes = csfield(cs.Const(b"\x28"))
    skeleton_container_flag: bytes | None = csfield(cs.Optional(cs.Const(b"\x31")))
    skeleton_container: SkeletonContainer | None = csfield(
        cs.If(
            lambda ctx: ctx.skeleton_container_flag, DataclassStruct(SkeletonContainer)
        )
    )


@dataclass
class Key(DataclassMixin):
    models: list[PointContainer] = csfield(
        cs.Array(cs.this._._.header.groups_per_key, DataclassStruct(PointContainer))
    )


@dataclass
class AnimBody(DataclassMixin):
    keys: list[Key] = csfield(cs.Array(cs.this._.header.num_keys, DataclassStruct(Key)))


@dataclass
class Footer(DataclassMixin):
    const_2f: bytes = csfield(cs.Const(b"\x2F"))


@dataclass
class BafIni:
    num_keys: int
    key_times: list[float] | None
    loop_in: int | None
    loop_out: int | None

    @classmethod
    def from_file(cls, file: Path):
        if not file.exists():
            raise FileNotFoundError(f"File {file} does not exist.")

        baf_ini_file = cls.__new__(cls)

        config = configparser.ConfigParser()
        config.read(file)

        if not config.has_section(BAF_INI_FILE_SECTION):
            raise KeyError(f"Section {BAF_INI_FILE_SECTION} not found in config file.")

        baf_ini_file.num_keys = config.getint(
            BAF_INI_FILE_SECTION, BAF_INI_FILE_NUM_KEYS
        )
        if BAF_INI_FILE_KEYS in config[BAF_INI_FILE_SECTION]:
            baf_ini_file.key_times = [
                float(key_time_str) / 80
                for key_time_str in config.get(
                    BAF_INI_FILE_SECTION, BAF_INI_FILE_KEYS
                ).split(",")
            ]
        if BAF_INI_FILE_LOOP_IN in config[BAF_INI_FILE_SECTION]:
            baf_ini_file.loop_in = config.getint(
                BAF_INI_FILE_SECTION, BAF_INI_FILE_LOOP_IN
            )
        if BAF_INI_FILE_LOOP_OUT in config[BAF_INI_FILE_SECTION]:
            baf_ini_file.loop_out = config.getint(
                BAF_INI_FILE_SECTION, BAF_INI_FILE_LOOP_OUT
            )

        return baf_ini_file


@dataclass
class Baf(BaseConstruct):
    header: AnimHeader = csfield(DataclassStruct(AnimHeader))
    body: AnimBody = csfield(DataclassStruct(AnimBody))
    footer: Footer = csfield(DataclassStruct(Footer))
    baf_ini: BafIni | None = csfield(cs.Computed(lambda ctx: None))

    @property
    def keyframe_count(self) -> int:
        return self.header.num_keys

    def get_vertices_per_key(self) -> np.ndarray:
        vertices_per_key = []

        for key in self.body.keys:
            vertices = []

            for model in key.models:
                for vertex in model.vertices:
                    vertices.append([vertex.x, vertex.y, vertex.z])

            vertices_per_key.append(vertices)

        return np.array(vertices_per_key, dtype=np.float32)

    @property
    def format(self) -> SourceFormat:
        """Return the format of the construct."""

        return SourceFormat.BAF
