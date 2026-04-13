#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import types as types_mod
from collections import defaultdict
import inspect


class MultiMethod:
    _functions = defaultdict(dict)

    def __init__(self, name=None):
        self._name = name

    def __set_name__(self, owner, name):
        self._name = name

    def add_function(self, func, new_name=None):
        sig = inspect.signature(func)
        # [<class 'int'>, <class 'int'>]
        types = tuple([v.annotation for v in sig.parameters.values()][1:])
        if new_name is None:
            new_name = func.__name__
        func.__name__ = new_name
        self._functions[new_name][types] = func

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        def dispatcher(name, *args):
            # [<class 'int'>, <class 'int'>]
            types = tuple([type(arg) for arg in args])
            return self._functions[name][types](self, *args)

        return dispatcher
        # return types_mod.MethodType(self._functions["addxs"], instance)


def add1(self, x: int, y: int):
    return x + y


def add2(self, x: float, y: float):
    return x + y


class Spam:
    mm = MultiMethod()
    mm.add_function(add1, new_name="add")
    mm.add_function(add2, new_name="add")

    def __call__(self, function_name: str, *args):
        return self.mm(function_name, *args)


if __name__ == "__main__":
    spam = Spam()
    print(spam.mm("add", 1, 2))
    print(spam.mm("add", 10.01, 20.02))
