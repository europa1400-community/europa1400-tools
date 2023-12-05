from dataclasses import fields
from enum import Enum
from functools import wraps
from inspect import Parameter, signature
from pathlib import Path
from typing import Any, Callable, Optional, Type

from typer import Typer
from typer import main as typer_main
from typer.main import generate_enum_convertor, lenient_issubclass

from europa1400_tools.cli.base_options import BaseOptions
from europa1400_tools.models.gilde_path import GildePath


def determine_type_convertor(type_: Any) -> Optional[Callable[[Any], Any]]:
    convertor: Optional[Callable[[Any], Any]] = None
    if lenient_issubclass(type_, Path):
        convertor = param_path_convertor
    if lenient_issubclass(type_, Enum):
        convertor = generate_enum_convertor(type_)
    return convertor


def param_path_convertor(value: Optional[str] = None) -> Optional[GildePath]:
    if value is not None:
        return GildePath(value)
    return None


typer_main.determine_type_convertor = determine_type_convertor


def callback(typer_app: Typer, options_types: list[Type[BaseOptions]], *args, **kwargs):
    def decorator(__f):
        @wraps(__f)
        def wrapper(*__args, **__kwargs):
            if len(__args) > 0:
                raise RuntimeError("Positional arguments are not supported")

            for options_type in options_types:
                __kwargs = _patch_wrapper_kwargs(options_type, **__kwargs)

            return __f(*__args, **__kwargs)

        for options_type in options_types:
            _patch_command_sig(wrapper, options_type)

        return typer_app.callback(*args, **kwargs)(wrapper)

    return decorator


def command(typer_app, options_types: list[Type[BaseOptions]], *args, **kwargs):
    def decorator(__f):
        @wraps(__f)
        def wrapper(*__args, **__kwargs):
            if len(__args) > 0:
                raise RuntimeError("Positional arguments are not supported")

            for options_type in options_types:
                __kwargs = _patch_wrapper_kwargs(options_type, **__kwargs)

            return __f(*__args, **__kwargs)

        for options_type in options_types:
            _patch_command_sig(wrapper, options_type)

        return typer_app.command(*args, **kwargs)(wrapper)

    return decorator


def _patch_wrapper_kwargs(options_type: Type[BaseOptions], **kwargs):
    if (ctx := kwargs.get("ctx")) is None:
        raise RuntimeError("Context should be provided")

    common_opts_params: dict = {}

    if hasattr(options_type, "instance") and options_type.instance is not None:
        common_opts_params.update(options_type.instance.__dict__)

    for field in fields(options_type):
        if field.metadata.get("ignore", False):
            continue

        value = kwargs.pop(field.name)

        if value == field.default:
            continue

        common_opts_params[field.name] = value

    options_type(**common_opts_params)
    setattr(ctx, options_type.ATTRNAME, common_opts_params)

    return {"ctx": ctx, **kwargs}


def _patch_command_sig(__w, options_type: Type[BaseOptions]) -> None:
    sig = signature(__w)
    new_parameters = sig.parameters.copy()

    options_type_fields = fields(options_type)

    for field in options_type_fields:
        if field.metadata.get("ignore", False):
            continue
        new_parameters[field.name] = Parameter(
            name=field.name,
            kind=Parameter.KEYWORD_ONLY,
            default=field.default,
            annotation=field.type,
        )
    for kwarg in sig.parameters.values():
        if kwarg.kind == Parameter.KEYWORD_ONLY and kwarg.name != "ctx":
            if kwarg.name not in new_parameters:
                new_parameters[kwarg.name] = kwarg.replace(default=kwarg.default)

    new_sig = sig.replace(parameters=tuple(new_parameters.values()))
    setattr(__w, "__signature__", new_sig)
