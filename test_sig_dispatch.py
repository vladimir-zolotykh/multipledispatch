#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import os
import sys
import inspect


def bar1(x: float, y: float):
    pass


def bar2(x: int, y: int):
    pass


def bar3(s: str, n: int = 0):
    pass


def select(*args, **kwargs):
    _sig_cache = {f: inspect.signature(f) for f in [bar1, bar2, bar3]}
    for func in _sig_cache:
        sig = _sig_cache[func]
        try:
            sig.bind(*args, **kwargs)
            print(f"Best match {func.__name__}")
        except TypeError as exc:
            print(exc)


def test_select():
    # if __name__ == "__main__":
    select("hello")
