import copy
import dataclasses
import textwrap
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Callable, Optional, cast

import construct as cs
from construct_typed import DataclassMixin, DataclassStruct, csfield
from construct_typed.generic_wrapper import Construct, Context, ParsedType


def metacsfield(
    subcon: Construct[ParsedType, Any],
    doc: Optional[str] = None,
    parsed: Optional[Callable[[Any, Context], None]] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> ParsedType:
    """Return a csfield with metadata."""

    orig_subcon = subcon

    if (doc is not None) or (parsed is not None):
        if doc is not None:
            doc = textwrap.dedent(doc).strip("\n")
        subcon = cs.Renamed(subcon, newdocs=doc, newparsed=parsed)

    if orig_subcon.flagbuildnone is True:
        init = False
        default = None
    else:
        init = True
        default = dataclasses.MISSING

    if isinstance(orig_subcon, cs.Const):
        const_subcon: "cs.Const[Any, Any, Any, Any]" = orig_subcon
        default = const_subcon.value
    elif isinstance(orig_subcon, cs.Default):
        default_subcon: "cs.Default[Any, Any, Any, Any]" = orig_subcon
        if callable(default_subcon.value):
            default = None
        else:
            default = default_subcon.value

    if metadata is None:
        metadata = {}
    metadata["subcon"] = subcon

    return cast(
        ParsedType,
        dataclasses.field(
            default=default,
            init=init,
            metadata=metadata,
        ),
    )


def ignoredcsfield(
    subcon: Construct[ParsedType, Any],
    doc: Optional[str] = None,
    parsed: Optional[Callable[[Any, Context], None]] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> ParsedType:
    """Return a csfield with metadata."""

    if metadata is None:
        metadata = {}
    metadata["ignored"] = True

    return metacsfield(subcon, doc=doc, parsed=parsed, metadata=metadata)


_FIELDS = "__dataclass_fields__"


def _is_dataclass_instance(obj):
    """Returns True if obj is an instance of a dataclass."""
    return hasattr(type(obj), _FIELDS)


def asdict(obj, *, dict_factory=dict):
    if not _is_dataclass_instance(obj):
        raise TypeError("asdict() should be called on dataclass instances")
    return _asdict_inner(obj, dict_factory)


def _asdict_inner(obj, dict_factory):
    if _is_dataclass_instance(obj):
        result = []
        for f in fields(obj):
            if f.metadata.get("ignored", False) is True:
                continue
            value = _asdict_inner(getattr(obj, f.name), dict_factory)
            result.append((f.name, value))
        return dict_factory(result)
    elif isinstance(obj, tuple) and hasattr(obj, "_fields"):
        return type(obj)(*[_asdict_inner(v, dict_factory) for v in obj])
    elif isinstance(obj, (list, tuple)):
        return type(obj)(_asdict_inner(v, dict_factory) for v in obj)
    elif isinstance(obj, dict):
        return type(obj)(
            (_asdict_inner(k, dict_factory), _asdict_inner(v, dict_factory))
            for k, v in obj.items()
        )
    if isinstance(obj, Path):
        return str(obj)
    else:
        return copy.deepcopy(obj)


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


@dataclass
class Latin1String(DataclassMixin):
    """Structure of a string in latin-1 encoding."""

    _value_bytes: bytes = ignoredcsfield(cs.NullTerminated(cs.GreedyBytes))
    value: str = csfield(cs.Computed(lambda ctx: ctx._value_bytes.decode("latin-1")))
