#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from draugr.writers.writer import Writer

__author__ = "Christian Heider Nielsen"
__doc__ = """
Created on 27/04/2019

@author: cnheider
"""

__all__ = ["MockWriter"]


class MockWriter(Writer):
    """"""

    def _close(self, exc_type=None, exc_val=None, exc_tb=None):
        pass

    def _open(self):
        return self

    def _scalar(self, *args, **kwargs):
        pass


if __name__ == "__main__":
    with MockWriter() as w:
        w.scalar("a", 2)
