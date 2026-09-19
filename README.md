# Introduction

This package introduces a new data-structure that is mix of `frozendict` introduced in Python 3.15 ([PEP 814](https://peps.python.org/pep-0814/)) and `collections.defaultdict`, with small changes to the API to make it more usable.

# Install

You can install `frozendefaultdict` by using `pip`

```sh
python -m pip install frozendefaultdict
```

or any other Python package manager able to install from PyPI.

# API

The `frozendefaultdict` class implements the same API as `frozendict` (see [PEP 814](https://peps.python.org/pep-0814/)) up to a few changes that are noted below.

## Notable differences with `frozendict`

The constructor of `frozendefaultdict` has a keyword-only argument `default_value` that does not exist in the `frozendict` class.

The `frozendict` constructors using `**kwargs` (`frozendict(**kwargs)` and `frozendict(collection, **kwargs)`) are not supported for `frozendefaultdict`.

`frozendict` instances can be compared to `dict`. `frozendefaultdict` instances **cannot** be compared to `dict` (the comparison will always return `False`), and also **cannot** be compared to `defaultdict` due to the fact that `defaultdict` has a `default_factory` where `frozendefaultdict` has a `default_value`.

`frozendefaultdict` has the following additional properties and methods:
  1. `has_default_value` that is `True` when the `frozendefaultdict` instance has a default value.
  2. `default_value` that returns the default value of the instance or `None`.
  3. `map_keys` that returns a new `frozendefaultdict` instance with new keys but the same values.
  4. `map_values` that returns a new `frozendefaultdict` instance with new values (and default value) but the same keys.
  5. `map_keys_if_present` that returns a new `frozendefaultdict` instance with new keys and (potentially a subset of) the same values.

## Notable differences with `defaultdict`

The `frozendefaultdict` class takes a default **value** as argument instead of a **callable** that returns the default value. This is mainly to make `frozendefaultdict` hashable and comparable with other `frozendefaultdict` instances without relying on function identity (`id()`) which breaks as soon as `lambda`s are used.

If **callables** were used, the class would have no reliable way to hash or compare the provided callable (using the `id()` of the callable is very brittle, see below, and using the callable code from `inspect` would also break with `a` and `c` in the exemple below). 

For example, with Python `3.10`, the following code

```py
a = lambda: 4
b = lambda: 4
c = lambda: 2 + 2
print(id(a))
print(id(b))
print(id(c))
```

outputs `3` different numbers, which makes the `id()` function a bad implementation for `hash()`.

# Examples

```py
from frozendefaultdict import frozendefaultdict

fdd = frozendefaultdict({0: 1, 4: 2}, default_value=98)
print(fdd)
# frozendefaultdict({0: 1, 4: 2}, default_value=98)

fdd2 = fdd | {0: 3}
print(fdd2)
# frozendefaultdict({0: 3, 4: 2}, default_value=98)

fdd3 = frozendefaultdict[int, int]({}, default_value=3)
fdd4 = fdd | fdd3
print(fdd4)
# frozendefaultdict({0: 1, 4: 2}, default_value=3)

print(fdd[0])
# 1
print(fdd[-1])
# 98

print(fdd.has_default_value)
# True
print(fdd.default_value)
# 98

fdd5 = fdd.map_keys(lambda i: i + 5)
print(fdd5)
# frozendefaultdict({5: 1, 9: 2}, default_value=98)

fdd6 = fdd.map_values(lambda i: i - 5)
print(fdd6)
# frozendefaultdict({0: -4, 4: -3}, default_value=93)

fdd7 = fdd.map_keys_if_present({0: 4, 923874: 9023784})
print(fdd7)
# frozendefaultdict({4: 1}, default_value=98)
```