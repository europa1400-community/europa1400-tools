"""Construct structures for SBF files."""

from dataclasses import dataclass

import construct as cs
from construct_typed import DataclassMixin, DataclassStruct, csfield

from europa_1400_tools.const import SoundbankType, SoundType
from europa_1400_tools.construct.base_construct import BaseConstruct


@dataclass
class SoundDefinition(DataclassMixin):
    """Structure of sound definition."""

    sound_type_int: int = csfield(cs.Int32ul)
    sound_type: SoundType = csfield(
        cs.Computed(lambda this: SoundType(this.sound_type_int))
    )
    length: int = csfield(cs.Int32ul)
    magic: int = csfield(cs.Int32ul)


@dataclass
class SoundbankHeader(DataclassMixin):
    """Structure of soundbank header."""

    sound_count: int = csfield(cs.Int32ul)
    magic1: int = csfield(cs.Int32ul)
    magic2: int = csfield(cs.Int32ul)


@dataclass
class SoundbankDefinition(DataclassMixin):
    """Structure of soundbank definition."""

    address: int = csfield(cs.Int32ul)
    name: str = csfield(cs.PaddedString(50, "ascii"))
    soundbank_type_int: int = csfield(cs.Int16ul)
    soundbank_type: SoundbankType = csfield(
        cs.Computed(lambda this: SoundbankType(this.soundbank_type_int))
    )
    padding: bytes = csfield(cs.Bytes(8))


@dataclass
class Soundbank(DataclassMixin):
    """Structure of soundbank."""

    soundbank_definition: SoundbankDefinition = csfield(
        cs.Computed(
            lambda ctx: ctx._.soundbank_definitions[
                # pylint: disable=protected-access
                ctx._index
            ]
        )
    )
    soundbank_header: SoundbankHeader | None = csfield(
        cs.If(
            cs.this.soundbank_definition.soundbank_type == SoundbankType.MULTI,
            DataclassStruct(SoundbankHeader),
        )
    )
    sound_count: int = csfield(
        cs.Computed(
            lambda this: 1
            if this.soundbank_definition.soundbank_type == SoundbankType.SINGLE
            else this.soundbank_header.sound_count
        )
    )
    sound_definitions: list[SoundDefinition] = csfield(
        cs.Array(cs.this.sound_count, DataclassStruct(SoundDefinition))
    )
    sounds: list[bytes] = csfield(
        cs.Array(
            cs.this.sound_count,
            cs.Bytes(
                # pylint: disable=protected-access
                lambda this: this.sound_definitions[this._index].length
            ),
        )
    )


@dataclass
class Sbf(BaseConstruct):
    """Structure of SBF file."""

    name: str = csfield(cs.PaddedString(308, "ascii"))
    soundbank_count: int = csfield(cs.Int32ul)
    magic: bytes = csfield(cs.Bytes(4))
    padding: bytes = csfield(cs.Bytes(8))
    soundbank_definitions: list[SoundbankDefinition] = csfield(
        cs.Array(cs.this.soundbank_count, DataclassStruct(SoundbankDefinition))
    )
    soundbanks: list[Soundbank] = csfield(
        cs.Array(cs.this.soundbank_count, DataclassStruct(Soundbank))
    )
