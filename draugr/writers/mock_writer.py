#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from draugr.writers.writer import Writer

__author__ = "cnheider"
__doc__ = ""


class MockWriter(Writer):
    def _scalar(self, tag: str, value: float, step: int):
        pass