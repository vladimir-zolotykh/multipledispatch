#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from typing import Any
import sys
import types as typesmod
import inspect
import pytest


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
        self._name = name
        self._types = {}  # signature -> method dict
        self._signatures = {}

    # def add_default_types(self, types):
    #     n = len(types)
    #     for typ in self._types:
    #         if typ[:n] == types:
    #             types = tuple(types + typ[n:])
    #     return types

    def select_signatue(
        self, *args: list[Any], **kwargs: dict[str, Any]
    ) -> tuple[type, ...]:
        for key, sig in self._signatures.items():
            try:
                sig.bind(*args, **kwargs)
                return tuple([parm.annotation for parm in sig.parameters.values()])
            except TypeError:
                pass  # continue checking
        raise TypeError(f"No matching method for {args}, {kwargs}")

    def __call__(self, *args, **kwargs):
        types = tuple([type(arg) for arg in args][1:])
        try:
            omethod = self._types[types]
        except KeyError:
            types = self.select_signatue(*args, **kwargs)
            # types = self.add_default_types(types)
            omethod = self._types[types[1:]]
        return omethod(*args, **kwargs)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return typesmod.MethodType(self, instance)

    def register(self, omethod):  # overloaded method
        sig = inspect.signature(omethod)
        types = tuple([v.annotation for v in sig.parameters.values()][1:])
        self._types[types] = omethod
        self._signatures[self._name] = sig


class MultiMeta(type):
    @classmethod
    def __prepare__(metacls, name, bases, **kwargs):
        return MultiDict()


class Spam(metaclass=MultiMeta):
    def bar(self, x: int, y: int):
        # print("Bar 1: ", x, y)
        return f"Bar 1: {x}, {y}"

    def bar(self, s: str, n: int = 0):  # noqa: F811
        # print("Bar 2: ", s, n)
        return f"Bar 2: {s}, {n}"


import time  # noqa: E402


class Date(metaclass=MultiMeta):
    def __init__(self, year: int, month: int, day: int):
        self.year = year
        self.month = month
        self.day = day

    def __init__(self):  # noqa: F811
        t = time.localtime()
        self.__init__(t.tm_year, t.tm_mon, t.tm_mday)


def test_basic():
    s = Spam()
    assert s.bar(3, 5) == "Bar 1: 3, 5"
    assert s.bar("hello", 22) == "Bar 2: hello, 22"
    assert s.bar("hello") == "Bar 2: hello, 0"
    d = Date(2012, 12, 21)
    assert (d.year, d.month, d.day) == (2012, 12, 21)
    e = Date()

    def today():
        t = time.localtime()
        return t.tm_year, t.tm_mon, t.tm_mday

    assert (e.year, e.month, e.day) == today()


if __name__ == "__main__":
    pytest.main(sys.argv)
