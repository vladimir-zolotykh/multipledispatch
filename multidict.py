#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from typing import Any
import time
import types as typesmod
import inspect
from typing import get_type_hints
import unittest


class MultiDict(dict):
    def __setitem__(self, key, value):
        if key not in self:
            super().__setitem__(key, value)
            return
        ov_value = self[key]
        if isinstance(ov_value, MultiMethod):
            mm = ov_value
        else:
            mm = MultiMethod(key)
            mm.register(ov_value)
        mm.register(value)
        super().__setitem__(key, mm)


class MultiMethod:
    def __init__(self, name=None):
        self._name = name
        self._ovmethods = []

    def select_overloaded_method(
        self, *args: list[Any], **kwargs: dict[str, Any]
    ) -> tuple[type, ...]:
        """Iterate all registered methods in self._ovmethods. Return
        one that matches *args, **kwargs. Raise TypeError if not
        found.

        """
        for sig, ovmethod in self._ovmethods:
            hints = get_type_hints(ovmethod)
            try:
                bound = sig.bind(*args, **kwargs)
                bound.apply_defaults()
                for arg_name, arg_value in bound.arguments.items():
                    if arg_name == "self":
                        continue
                    expected = hints[arg_name]
                    if arg_name in hints:
                        expected = hints[arg_name]
                        if not isinstance(arg_value, expected):
                            raise TypeError()
                return ovmethod
            except TypeError:
                pass  # continue checking
        raise TypeError(f"No matching method {self._name} for {args}, {kwargs}")

    def __call__(self, *args, **kwargs):
        ovmethod = self.select_overloaded_method(*args, **kwargs)
        return ovmethod(*args, **kwargs)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return typesmod.MethodType(self, instance)

    def register(self, ovmethod):  # overloaded method
        sig = inspect.signature(ovmethod)
        self._ovmethods.append((sig, ovmethod))


class MultiMeta(type):
    @classmethod
    def __prepare__(metacls, name, bases, **kwargs):
        return MultiDict()


class Spam(metaclass=MultiMeta):
    """
    >>> s = Spam()
    >>> print(s.bar(3, 5))
    Bar 1: 3, 5
    >>> print(s.bar("hello", 22))
    Bar 1: hello, 22
    >>> print(s.bar("hello"))
    Bar 2: hello, 0
    """

    def bar(self, x: int, y: int):
        return f"Bar 1: {x}, {y}"

    def bar(self, s: str, n: int = 0):  # noqa: F811
        return f"Bar 2: {s}, {n}"


class Date(metaclass=MultiMeta):
    """
    >>> d = Date(2012, 12, 21)
    >>> print(d)
    Date(2012, 12, 21)
    >>> e = Date()
    >>> print(e)  # doctest: +ELLIPSIS
    Date(..., ..., ...)
    """

    def __init__(self, year: int, month: int, day: int):
        self.year = year
        self.month = month
        self.day = day

    def __init__(self):  # noqa: F811
        t = time.localtime()
        self.__init__(t.tm_year, t.tm_mon, t.tm_mday)

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([str(getattr(self, attr)) for attr in self.__dict__])})"


class TestSpam(unittest.TestCase):
    def setUp(self):
        self.s = Spam()

    def test_type_mismatch_raises(self):
        with self.assertRaises(TypeError):
            self.s.bar(3, "bad")

    def test_no_matching_overload(self):
        with self.assertRaises(TypeError):
            self.s.bar(3.14, 2.71)

    def test_kwargs_dispatch(self):
        self.assertEqual(self.s.bar(s="hi", n=5), "Bar 2: hi, 5")

    def test_partial_kwargs(self):
        self.assertEqual(self.s.bar(s="hi"), "Bar 2: hi, 0")

    def test_bound_unbound_equivalence(self):
        self.assertEqual(self.s.bar(1, 2), Spam.bar(self.s, 1, 2))

    def test_method_is_descriptor(self):
        self.assertTrue(callable(Spam.bar))
        self.assertTrue(callable(self.s.bar))

    def test_error_message_contains_name(self):
        try:
            self.s.bar(1.1, 2.2)
        except TypeError as e:
            self.assertIn("bar", str(e))


class TestDate(unittest.TestCase):
    def test_explicit_init(self):
        d = Date(2020, 1, 2)
        self.assertEqual((d.year, d.month, d.day), (2020, 1, 2))

    def test_no_args_init_matches_today(self):
        t = time.localtime()
        d = Date()
        self.assertEqual((d.year, d.month, d.day), (t.tm_year, t.tm_mon, t.tm_mday))

    def test_repr_format(self):
        d = Date(2000, 2, 3)
        self.assertEqual(repr(d), "Date(2000, 2, 3)")

    def test_invalid_signature(self):
        with self.assertRaises(TypeError):
            Date(1)

    def test_type_validation(self):
        with self.assertRaises(TypeError):
            Date("2020", "01", "02")


if __name__ == "__main__":
    unittest.main()
