from dataclasses import dataclass

import construct as cs
from construct_typed import DataclassStruct, csfield

from europa_1400_tools.construct.base_construct import BaseConstruct
from europa_1400_tools.construct.common import Latin1String
from europa_1400_tools.helpers import strip_non_ascii


@dataclass
class Txs(BaseConstruct):
    """Structure of TXS file."""

    magic: int = csfield(cs.Int32ul)
    num1: int = csfield(cs.Int32ul)
    num2: int = csfield(cs.Int32ul)

    _texture_names: list[Latin1String] = csfield(
        cs.Array(lambda ctx: ctx.num1 * ctx.num2, DataclassStruct(Latin1String))
    )

    @property
    def texture_names(self) -> list[str]:
        return {
            texture_name.value.lower()
            for texture_name in self._texture_names
            if texture_name.value != ""
        }

    @property
    def texture_names_normalized(self) -> list[str]:
        return {
            strip_non_ascii(texture_name.value.lower())
            for texture_name in self._texture_names
            if texture_name.value != ""
        }
