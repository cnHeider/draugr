#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from draugr import Writer

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 9/14/19
           """


class VisdomWriter(Writer):
    def _scalar(self, tag: str, value: float, step: int):
        pass

    def _close(self, exc_type=None, exc_val=None, exc_tb=None):
        pass

    def _open(self):
        pass