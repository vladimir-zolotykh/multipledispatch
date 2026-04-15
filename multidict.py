#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import types as typesmod
import inspect


class MultiDict(dict):
    def __setitem__(self, key, value):
        if key.startswith("__") or key not in self:
            super().__setitem__(key, value)
            return
        ovalue = self[key]
        if isinstance(ovalue, MultiMethod):
            mm = ovalue
        else:
            mm = MultiMethod()
            mm.register(ovalue)
        mm.register(value)
        super().__setitem__(key, mm)


class MultiMethod:
    def __init__(self, name=None):
        self._name = name
        self._types = {}  # signature -> method dict

    def __call__(self, *args, **kwargs):
        types = tuple([type(arg) for arg in args][1:])
        omethod = self._types[types]
        omethod(*args, **kwargs)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return typesmod.MethodType(self, instance)

    def register(self, omethod):  # overloaded method
        sig = inspect.signature(omethod)
        types = tuple([v.annotation for v in sig.parameters.values()][1:])
        self._types[types] = omethod


class MultiMeta(type):
    @classmethod
    def __prepare__(metacls, name, bases, **kwargs):
        return MultiDict()


class Spam(metaclass=MultiMeta):
    def bar(self, x: int, y: int):
        print("Bar 1: ", x, y)

    def bar(self, s: str, n: int = 0):  # noqa: F811
        print("Bar 2: ", s, n)


if __name__ == "__main__":
    s = Spam()
    print(s.bar(3, 5))
    print(s.bar("hello", 22))
