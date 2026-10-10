# CHANGELOG

## Unreleased

### Breaking changes

#### Default value interface

The handling of default values have been reworked to allow `None` values. Now, if the user does not provide a default value when constructing the `frozendefaultdict`, calling the `.default_value` property raises an exception. The value `None` is not used as a sentinel to mean "no default value" any more, and so can be used as a regular default value.

Previously, the following interface was possible:

```py
fdd = frozendefaultdict({})
assert not fdd.has_default_value
assert fdd.default_value is None
assert fdd == frozendefaultdict({}, default_value=None)
```

Now, the above raises a `NoDefaultValueProvidedError` at line 3 when `fdd.default_value` is called. Instead, the following behaviour is implemented:

```py
fdd = frozendefaultdict({})
assert not fdd.has_default_value
# The following raises a NoDefaultValueProvidedError exception
# fdd.default_value
none_default = frozendefaultdict({}, default_value=None)
assert fdd != none_default
assert none_default.default_value is None
```

#### Removal of `frozendefaultdict.copy` and `frozendefaultdict.deepcopy`

The methods `frozendefaultdict.__copy__` and `frozendefaultdict.__deepcopy__` are already implemented and fulfil the same purpose while being more idiomatic. `frozendefaultdict.copy` and `frozendefaultdict.deepcopy` were only duplicating the implementation of `frozendefaultdict.__copy__` and `frozendefaultdict.__deepcopy__`, so they have been removed. 

The following code

```py
fdd = frozendefaultdict({})
fdd_copy = fdd.copy()
fdd_deep = fdd.deepcopy()
```

should now be replaced with

```py
from copy import copy, deepcopy

fdd = frozendefaultdict({})
fdd_copy = copy(fdd)
fdd_deep = deepcopy(fdd)
```

### Features

- Default value of a `frozendefaultdict` can now be `None`.

## `v0.1.0`

### Features
- Initial commit introducing the package ([`fd0f59b`](https://github.com/nelimee/frozendefaultdict/commit/fd0f59b6650c1b16c3e5446b8d5e7327c17ebaa0))
- Improve typing expressiveness ([`2c84af7`](https://github.com/nelimee/frozendefaultdict/commit/2c84af78947676e5b8a799cd6ddf82af74b8628a))

### Bug Fixes
- Release CI ([#4](https://github.com/nelimee/frozendefaultdict/pull/4), [`df6b429`](https://github.com/nelimee/frozendefaultdict/commit/df6b429b51e8011612d8762210999ede50ca8c14))
- Use bash shell for ci tests on windows ([#5](https://github.com/nelimee/frozendefaultdict/pull/5), [`be31e23`](https://github.com/nelimee/frozendefaultdict/commit/be31e23f617d4dfd41c803b978acd727c4d3c672))

### Documentation
- Improve code of conduct and contributing guidelines ([`aba472b`](https://github.com/nelimee/frozendefaultdict/commit/aba472b596c958558d542825a69193e3e1ecd24b))
- Improve LLM-related documentation ([`ab323f1`](https://github.com/nelimee/frozendefaultdict/commit/ab323f11215e81ecded7dbecd143a117039f2ef2))
- Update documentation and doctest ([`32856d7`](https://github.com/nelimee/frozendefaultdict/commit/32856d7ac5f955feca1aef7219069cc7d63c5237))
- Update LLM instructions ([`c3ddb99`](https://github.com/nelimee/frozendefaultdict/commit/c3ddb99a2cb1e5cfc7d7afe46953dd6ffe6aec78))
- Update README for attribution ([`bc9c7c9`](https://github.com/nelimee/frozendefaultdict/commit/bc9c7c978f1628c6ea30d38e3092583ed9869ac2))
- Update README on LLM usage ([`cebbaf7`](https://github.com/nelimee/frozendefaultdict/commit/cebbaf7664147f3f52d7035df428472dd73f8aec))


<!--- Generated with `uvx --from "python-semantic-release>=10,<11" semantic-release -vv changelog` -->