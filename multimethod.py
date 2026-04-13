#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import types


class MultiMethod:
    _functions = {}

    def __init__(self, name=None):
        self._name = name

    def __set_name__(self, owner, name):
        self._name = name

    def add_function(self, func):
        self._functions[func.__name__] = func

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return types.MethodType(self._functions["addxs"], instance)


def addxs(self, x: int, s: str):
    return str(x) + s


class Spam:
    sum = MultiMethod()
    sum.add_function(addxs)

    def __call__(self, x: int, s: str):
        print(self.sum(x, s))


if __name__ == "__main__":
    spam = Spam()
    spam(11, " hello")
