#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 04-01-2021
           """

import os
import sys

__all__ = ["get_backend_module"]

from types import ModuleType


def get_backend_module(project_name) -> ModuleType:
    """Returns the backend module."""
    import importlib

    backend_name = os.environ.get("NOTUS_BACKEND", None)
    modules = []
    if backend_name is not None:
        modules = [backend_name]
    elif sys.platform == "darwin":
        modules = ["darwin"]
    elif sys.platform == "win32":
        modules = ["win10"]
    else:
        modules = ["appindicator", "gtk", "xorg"]

    errors = []
    for module in modules:
        try:
            return importlib.import_module(f"{project_name}.{module}")
        except ImportError as e:
            errors.append(e)

    raise ImportError(
        f'{sys.platform} platform is not supported: {"; ".join(str(e) for e in errors)}'
    )
