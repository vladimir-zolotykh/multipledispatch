#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from typing import Any
import sys
import time
import types as typesmod
import inspect

# import pytest


class MultiDict(dict):
    def __setitem__(self, key, value):
        if key not in self:
            super().__setitem__(key, value)
            return
        ovalue = self[key]
        if isinstance(ovalue, MultiMethod):
            mm = ovalue
        else:
            mm = MultiMethod(key)
            mm.register(ovalue)
        mm.register(value)
        super().__setitem__(key, mm)


class MultiMethod:
    def __init__(self, name=None):
        # self.__name__ = name
        self._signatures = []

    def select_signatue(
        self, *args: list[Any], **kwargs: dict[str, Any]
    ) -> tuple[type, ...]:
        for sig, omethod in self._signatures:
            try:
                sig.bind(*args, **kwargs)
                return omethod
            except TypeError:
                pass  # continue checking
        raise TypeError(f"No matching method for {args}, {kwargs}")

    def __call__(self, *args, **kwargs):
        omethod = self.select_signatue(*args, **kwargs)
        return omethod(*args, **kwargs)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return typesmod.MethodType(self, instance)

    def register(self, omethod):  # overloaded method
        sig = inspect.signature(omethod)
        self._signatures.append((sig, omethod))


class MultiMeta(type):
    @classmethod
    def __prepare__(metacls, name, bases, **kwargs):
        return MultiDict()


class Spam(metaclass=MultiMeta):
    def bar(self, x: int, y: int):
        return f"Bar 1: {type(x) = }, {type(y) = }, {x}, {y}"

    def bar(self, s: str, n: int = 0):  # noqa: F811
        return f"Bar 2: {s}, {n}"


class Date(metaclass=MultiMeta):
    def __init__(self, year: int, month: int, day: int):
        self.year = year
        self.month = month
        self.day = day

    def __init__(self):  # noqa: F811
        t = time.localtime()
        self.__init__(t.tm_year, t.tm_mon, t.tm_mday)


if __name__ == "__main__":
    s = Spam()
    print(s.bar(3, 5))
    print(s.bar("hello", 22))
    print(s.bar("hello"))
    d = Date(2012, 12, 21)
    print(d)
    e = Date()
    print(e)
