#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK


class MultiDict(dict):
    def __setitem__(self, key, value):
        if not key.startswith("__"):
            print(f"{key = }, {value = }")
        super().__setitem__(key, value)


class MultiMeta(type):
    def __new__(mcls, clsname, bases, clsdict):
        for attr, value in clsdict.items():
            if not attr.startswith("__"):
                print(f"{attr = }, {value = }")
        return super().__new__(mcls, clsname, bases, clsdict)

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
