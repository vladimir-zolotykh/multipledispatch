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
    functions = [bar1, bar2, bar3]
    for func in functions:
        sig = inspect.signature(func)
        try:
            sig.bind(*args, **kwargs)
            print(f"Best match {func.__name__}")
        except TypeError as exc:
            print(f"{func.__name__}: {args, kwargs} - {exc}")
            # with open(
            #     f".{os.path.splitext(os.path.basename(__file__))[0]}.log", "w"
            # ) as f:
            #     print(exc, file=f)


if __name__ == "__main__":
    # def test_select():
    select("hello")
