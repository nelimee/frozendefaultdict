"""Frozen (immutable, hashable) variant of :class:`~collections.defaultdict`.

Adapted from ``tqec`` under the Apache 2.0 License.
https://github.com/tqec/tqec/blob/main/src/tqec/utils/frozendefaultdict.py
"""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable, Iterator, Mapping
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Final, TypeVar

from typing_extensions import override

K = TypeVar("K", bound=Hashable)
Kp = TypeVar("Kp", bound=Hashable)
V_co = TypeVar("V_co", covariant=True)
Vp = TypeVar("Vp")


@dataclass(frozen=True)
class _NoDefaultProvided:
    """This class exists as a replacement to Python 3.15 ``sentinel``.

    Python 3.15 introduced the ``sentinel`` builtin (see PEP 661
    https://peps.python.org/pep-0661/ and the official documentation
    https://docs.python.org/3.15/builtins/functions.html#sentinel). Because
    ``frozendefaultdict`` supports Python 3.11 and above, it cannot yet use Python 3.15
    features.

    ``typing_extensions.sentinel`` exists, but type checkers do not seem to support it
    well yet.
    """


_NO_DEFAULT_PROVIDED: Final = _NoDefaultProvided()


class NoDefaultValueProvidedError(RuntimeError):
    pass


class frozendefaultdict(Mapping[K, V_co]):  # noqa: N801
    """Immutable, hashable mapping with an optional default value.

    Unlike :class:`~collections.defaultdict`, accessing a missing key does **not**
    mutate the container, it either returns the pre-configured ``default_value`` or
    raises :class:`KeyError`.

    Because the internal state never changes, and if the stored values (including the
    default value) are hashable, instances are hashable and safe to use as dictionary
    keys or inside sets.

    This class stores a shallow copy of the provided mapping. This means that any
    modification to the mapping used to initialise it will not be reflected on the
    :class:`frozendefaultdict` instance, but any modification to keys or values will be.
    It is the user responsibility to ensure that keys are not mutated.

    Examples:
        >>> # Overview of the API
        >>> mapping = {"a": 1, "b": 2, "c": {0: 1}}
        >>> fdd = frozendefaultdict(mapping, default_value=0)
        >>> fdd["a"]
        1
        >>> fdd["c"]
        {0: 1}
        >>> fdd["missing"]
        0
        >>> "missing" in fdd  # the above line did not add the key, unlike defaultdict
        False
        >>> mapping["d"] = 1
        >>> fdd["d"]  # mutating the mapping doesn't affect the frozendefaultdict
        0
        >>> mapping["c"][0] = 78
        >>> fdd["c"]  # only a shallow copy is performed, the stored value is modified.
        {0: 78}
        >>> # Different ways to create an instance
        >>> frozendefaultdict()
        frozendefaultdict({})
        >>> frozendefaultdict(None)
        frozendefaultdict({})
        >>> frozendefaultdict({"a": 1, "b": 2})
        frozendefaultdict({'a': 1, 'b': 2})
        >>> frozendefaultdict([("x", 10), ("y", 20)])
        frozendefaultdict({'x': 10, 'y': 20})
        >>> frozendefaultdict(default_value=1)
        frozendefaultdict({}, default_value=1)
        >>> frozendefaultdict({"a": 1}, default_value=None)
        frozendefaultdict({'a': 1}, default_value=None)

    Args:
        arg: Initial data, either a mapping or an iterable of ``(key, value)`` pairs.
            Keys absent from ``arg`` will be implicitly associated with
            ``default_value`` if it is provided. Keys and values are not copied, it
            is the responsibility of the user to ensure that keys are not mutated.
        default_value: Value returned (without copying) when a key not present in
            ``arg`` is queried. If not provided, missing-key access raises
            :class:`KeyError`.
    """

    def __init__(
        self,
        arg: Mapping[K, V_co] | Iterable[tuple[K, V_co]] | None = None,
        *,
        default_value: V_co | _NoDefaultProvided = _NO_DEFAULT_PROVIDED,
    ) -> None:
        super().__init__()
        self._dict: dict[K, V_co] = dict(arg) if arg is not None else {}
        self._default_value = default_value

    # region Required abstract method

    @override
    def __len__(self) -> int:
        """Return the number of elements (excluding the default value) in the instance.

        Examples:
            >>> len(frozendefaultdict())
            0
            >>> len(frozendefaultdict(default_value=9))
            0
            >>> len(frozendefaultdict({"a": 3, "b": 5}))
            2
            >>> len(frozendefaultdict(enumerate(range(567))))
            567
        """
        return len(self._dict)

    @override
    def __iter__(self) -> Iterator[K]:
        """Iterate on the keys of the dictionary.

        Examples:
            >>> tuple(frozendefaultdict())
            ()
            >>> tuple(frozendefaultdict(default_value=9))
            ()
            >>> tuple(frozendefaultdict({"a": 3, "b": 5}))
            ('a', 'b')
            >>> tuple(frozendefaultdict(enumerate(range(10))))
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        """
        return iter(self._dict)

    @override
    def __contains__(self, key: object) -> bool:
        """Return ``True`` if the provided ``key`` is present in the instance.

        Examples:
            >>> "a" in frozendefaultdict()
            False
            >>> 9 in frozendefaultdict(default_value=9)
            False
            >>> "a" in frozendefaultdict({"a": 3, "b": 5})
            True
            >>> "c" in frozendefaultdict({"a": 3, "b": 5})
            False
            >>> 543 in frozendefaultdict(enumerate(range(567)))
            True

        Args:
            key: key to check.

        Returns:
            ``True`` if ``key`` is in ``self.keys()`` else ``False``.
        """
        return self._dict.__contains__(key)

    @override
    def __getitem__(self, key: K) -> V_co:
        """Return the value associated to ``key`` if it is contains in ``self``, else
        the ``default_value`` if it was set at the instance creation, else raises.

        Examples:
            >>> only_default = frozendefaultdict(default_value="default")
            >>> [
            ...     only_default[obj]
            ...     for obj in [1, "a", object(), True, frozendefaultdict()]
            ... ]
            ['default', 'default', 'default', 'default', 'default']
            >>> # Returning the default value does not mutate (unlike defaultdict).
            >>> only_default
            frozendefaultdict({}, default_value='default')
            >>> no_default = frozendefaultdict({"a": 3, "b": 5})
            >>> no_default["a"]
            3
            >>> no_default["unknown key"]
            Traceback (most recent call last):
            ...
            KeyError: 'unknown key'

        Args:
            key: key used to find the value that should be recovered.

        Raises:
            KeyError: if ``key not in self`` and the ``default_value`` argument was left
                to its default value at the creation of ``self``.

        Returns:
            The value associated to ``key`` if it is contained in ``self``, else the
            ``default_value`` if it was set at the instance creation.
        """
        try:
            return self._dict[key]
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key: K) -> V_co:
        """Return the default value, or raise :class:`KeyError`.

        Called by :meth:`__getitem__` when ``key`` is not in the mapping. Returns
        ``default_value`` (without copying) if it was set on instance creation, else
        raises :class:`KeyError`.

        Args:
            key: the missing key for which a default value should be generated. Ignored
                by this implementation, except when raising a :class:`KeyError`.

        Raises:
            KeyError: if ``self._default_value`` was not set at the instance creation.

        Returns:
            The default value ``self._default_value`` as reference if it was not set at
            instance creation.
        """
        if isinstance(self._default_value, _NoDefaultProvided):
            raise KeyError(key)
        return self._default_value

    # endregion

    # region Convenience methods

    def __or__(self, other: Mapping[Kp, Vp]) -> frozendefaultdict[K | Kp, V_co | Vp]:
        """Merge with ``other``, returning a new :class:`frozendefaultdict`.

        This method has the same semantic has ``dict.__or__`` (``self | other``). In
        particular, keys that appear in both ``self`` and ``other`` will be associated
        to the value in ``other`` (``other`` overwrites ``self``). This also applies to
        the stored ``default_value``.

        Examples:
            >>> no_default = frozendefaultdict({"a": 1, "b": 2})
            >>> with_default = frozendefaultdict({"a": 42, "c": 3}, default_value=53)
            >>> no_default | with_default
            frozendefaultdict({'a': 42, 'b': 2, 'c': 3}, default_value=53)
            >>> with_default | no_default
            frozendefaultdict({'a': 1, 'c': 3, 'b': 2})
            >>> with_default | {"a": 2, "b": 45}
            frozendefaultdict({'a': 2, 'c': 3, 'b': 45}, default_value=53)

        Args:
            other: mapping to use to update a copy of ``self``.

        Returns:
            a new ``frozendefaultdict`` that has the keys and values of both ``self``
            and ``other``. If a key is present in both ``self`` and ``other``, the value
            of ``other`` takes precedence. The default value of the returned instance is
            the default value of ``other`` (even if it is not set) if ``other`` is a
            ``frozendefaultdict`` instance, else the default value of ``self``.
        """
        mapping = dict[K | Kp, V_co | Vp]()
        for self_key, self_value in self._dict.items():
            mapping[self_key] = self_value
        for other_key, other_value in other.items():
            mapping[other_key] = other_value
        return frozendefaultdict(
            mapping,
            default_value=(
                other._default_value
                if isinstance(other, frozendefaultdict)
                else self._default_value
            ),
        )

    def __ror__(self, other: Mapping[Kp, Vp]) -> frozendefaultdict[K | Kp, V_co | Vp]:
        """Merge with ``other``, returning a new :class:`frozendefaultdict`.

        This method has the same semantic has ``dict.__ror__`` (``other | self``). In
        particular, keys that appear in both ``self`` and ``other`` will be associated
        to the value in ``self`` (``self`` overwrites ``other``). This also applies to
        the stored ``default_value``.

        Examples:
            >>> no_default = frozendefaultdict({"a": 1, "b": 2})
            >>> with_default = frozendefaultdict({"a": 42, "c": 3}, default_value=53)
            >>> {"a": 1, "b": 2} | with_default
            frozendefaultdict({'a': 42, 'b': 2, 'c': 3}, default_value=53)
            >>> {"a": 42, "c": 3} | no_default
            frozendefaultdict({'a': 1, 'c': 3, 'b': 2})

        Args:
            other: mapping to use to update a copy of ``self``.

        Raises:
            AssertionError: if ``self`` is a ``frozendefaultdict`` as this case should
                be handled by ``frozendefaultdict.__or__``.

        Returns:
            a new ``frozendefaultdict`` that has the keys and values of both ``self``
            and ``other``. If a key is present in both ``self`` and ``other``, the value
            of ``self`` takes precedence. The default value of the returned instance is
            the default value of ``self``.
        """
        # We know for sure that ``other`` is not a ``frozendefaultdict`` (because else
        # ``other.__or__`` would have been called instead), so we assert it here just in
        # case.
        assert not isinstance(other, frozendefaultdict), (
            "Should be handled by other.__or__."
        )
        mapping: dict[K | Kp, V_co | Vp] = {}
        for key, value in other.items():
            mapping[key] = value
        for self_key, self_value in self._dict.items():
            mapping[self_key] = self_value
        return frozendefaultdict(mapping, default_value=self._default_value)

    def __hash__(self) -> int:
        """Return a hash of ``self``.

        Examples:
            >>> fdd1 = frozendefaultdict({"a": 1, "b": 2})
            >>> hash(fdd1) == hash(fdd1)
            True
            >>> fdd1_reverse = frozendefaultdict({"b": 2, "a": 1})
            >>> hash(fdd1) == hash(fdd1_reverse)
            True

        Returns:
            a hash of ``self``.
        """
        return hash((frozenset(self.items()), self._default_value))

    def __eq__(self, other: object) -> bool:
        """Check equality based on stored items *and* default value.

        Two instances are equal iff they contain the same key-value pairs and share the
        same ``default_value``. Comparison with non-:class:`frozendefaultdict` objects
        always returns ``False``.

        Examples:
            >>> fdd1 = frozendefaultdict({"a": 1, "b": 2})
            >>> fdd1 == fdd1
            True
            >>> fdd1 == {"a": 1, "b": 2}
            False
            >>> fdd1_reverse = frozendefaultdict({"b": 2, "a": 1})
            >>> fdd1 == fdd1_reverse
            True
            >>> fdd2 = frozendefaultdict({"a": 1, "b": 2}, default_value=None)
            >>> fdd1 == fdd2
            False
            >>> fdd3 = frozendefaultdict({"a": 1, "b": 3})
            >>> fdd3 == fdd1
            False
            >>> fdd4 = frozendefaultdict({"a": 1, "b": 2}, default_value=67)
            >>> fdd2 == fdd4
            False

        Args:
            other: mapping to compare ``self`` to.

        Returns:
            ``False`` if ``other`` is not a ``frozendefaultdict`` instance, else
            ``True`` if ``self`` and ``other`` represent the same mapping with the same
            default value.
        """
        if not isinstance(other, frozendefaultdict):
            return False
        return (
            self._default_value == other._default_value
        ) and self._dict == other._dict

    def __copy__(self) -> frozendefaultdict[K, V_co]:
        """Return a copy of ``self``.

        Because ``self`` is immutable, this method returns ``self`` without actually
        copying.

        Examples:
            >>> from copy import copy
            >>> fdd = frozendefaultdict({"a": ["mutable"], "b": 2})
            >>> fdd
            frozendefaultdict({'a': ['mutable'], 'b': 2})
            >>> fddcpy = copy(fdd)
            >>> fddcpy
            frozendefaultdict({'a': ['mutable'], 'b': 2})
            >>> fdd["a"].extend(("this", "was", "mutable"))
            >>> fdd
            frozendefaultdict({'a': ['mutable', 'this', 'was', 'mutable'], 'b': 2})
            >>> fddcpy
            frozendefaultdict({'a': ['mutable', 'this', 'was', 'mutable'], 'b': 2})

        Returns:
            ``self`` directly, which is as good as a copy of ``self`` because ``self``
            is immutable.
        """
        return self

    def __deepcopy__(self, memo: dict[int, Any]) -> frozendefaultdict[K, V_co]:
        """Return a deep-copy of ``self``.

        Examples:
            >>> from copy import deepcopy
            >>> fdd = frozendefaultdict({"a": ["mutable"], "b": 2})
            >>> fdd
            frozendefaultdict({'a': ['mutable'], 'b': 2})
            >>> fddcpy = deepcopy(fdd)
            >>> fddcpy
            frozendefaultdict({'a': ['mutable'], 'b': 2})
            >>> fdd["a"].extend(("this", "was", "mutable"))
            >>> fdd
            frozendefaultdict({'a': ['mutable', 'this', 'was', 'mutable'], 'b': 2})
            >>> fddcpy
            frozendefaultdict({'a': ['mutable'], 'b': 2})

        Returns:
            a deep-copy of ``self``.
        """
        return frozendefaultdict[K, V_co](
            deepcopy(self._dict, memo),
            default_value=deepcopy(self._default_value, memo),
        )

    def __repr__(self) -> str:
        default_string = ""
        if not isinstance(self._default_value, _NoDefaultProvided):
            default_string = f", default_value={self._default_value!r}"
        return f"{self.__class__.__name__}({self._dict!r}{default_string})"

    @property
    def has_default_value(self) -> bool:
        """Return ``True`` if a default value was provided.

        Examples:
            >>> frozendefaultdict({"a": 1, "b": 2}).has_default_value
            False
            >>> frozendefaultdict({"a": 1}, default_value=None).has_default_value
            True
            >>> frozendefaultdict({"a": 1}, default_value=1).has_default_value
            True

        Returns:
            ``True`` if ``self`` has a default value, else ``False``.
        """
        return not isinstance(self._default_value, _NoDefaultProvided)

    @property
    def default_value(self) -> V_co:
        """Return the default value provided at instance construction or raise if none
        was provided.

        Examples:
            >>> str(frozendefaultdict({"a": 1}, default_value=None).default_value)
            'None'
            >>> frozendefaultdict({"a": 1}, default_value=1).default_value
            1
            >>> frozendefaultdict({"a": 1, "b": 2}).default_value
            Traceback (most recent call last):
            ...
            frozendefaultdict.frozendefaultdict.NoDefaultValueProvidedError

        Raises:
            NoDefaultValueProvidedError: if the ``default_value`` argument was not
                provided at the creation of ``self``.

        Returns:
            the default value provided when the instance was created if it was provided,
            else raises an exception.
        """
        if isinstance(self._default_value, _NoDefaultProvided):
            raise NoDefaultValueProvidedError()
        return self._default_value

    def map_keys(self, func: Callable[[K], K]) -> frozendefaultdict[K, V_co]:
        """Return a new instance with every key replaced by ``func(key)``.

        Values and the default value stay unchanged.

        Examples:
            >>> fdd = frozendefaultdict({"a": 1}, default_value=None)
            >>> fdd.map_keys(lambda k: chr(ord(k) + 1))
            frozendefaultdict({'b': 1}, default_value=None)
            >>> fdd.map_keys(lambda k: k) == fdd
            True

        Args:
            func: A callable applied to each key.

        Returns:
            a new :class:`frozendefaultdict` with transformed keys.
        """
        return frozendefaultdict[K, V_co](
            {func(k): v for k, v in self.items()}, default_value=self._default_value
        )

    def map_values(self, func: Callable[[V_co], Vp]) -> frozendefaultdict[K, Vp]:
        """Return a new instance with every value replaced by ``func(value)``.

        If a default value is set, it is also transformed through ``func``. Keys stay
        unchanged.

        Examples:
            >>> fdd = frozendefaultdict({"a": 1}, default_value=None)
            >>> fdd.map_values(lambda v: v + 1 if v is not None else v)
            frozendefaultdict({'a': 2}, default_value=None)
            >>> fdd.map_values(lambda v: v + 1)
            Traceback (most recent call last):
            ...
            TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'
            >>> fdd_default = frozendefaultdict({"a": 1}, default_value=41)
            >>> fdd_default.map_values(lambda v: v + 1)
            frozendefaultdict({'a': 2}, default_value=42)
            >>> fdd_no_default = frozendefaultdict({"a": 1})
            >>> fdd_no_default.map_values(lambda v: v + 1)
            frozendefaultdict({'a': 2})

        Args:
            func: A callable applied to each value (and the default value, if present).

        Returns:
            a new :class:`frozendefaultdict` with transformed values.
        """
        default_value: Vp | _NoDefaultProvided = _NO_DEFAULT_PROVIDED
        if not isinstance(self._default_value, _NoDefaultProvided):
            default_value = func(self._default_value)
        return frozendefaultdict(
            {k: func(v) for k, v in self.items()}, default_value=default_value
        )

    def map_keys_if_present(self, mapping: Mapping[K, K]) -> frozendefaultdict[K, V_co]:
        """Rename keys using ``mapping``, keeping only keys present in ``mapping``.

        For each key ``k`` in ``self``, if ``k`` is also in ``mapping`` the entry is
        included with the new key ``mapping[k]``. Entries whose key is **not** in
        ``mapping`` are dropped. Extra keys in ``mapping`` that are absent from ``self``
        are ignored. The default value is preserved.

        Examples:
            >>> fdd = frozendefaultdict({"a": 1}, default_value=None)
            >>> fdd.map_keys_if_present({"a": "b"})
            frozendefaultdict({'b': 1}, default_value=None)
            >>> fdd.map_keys_if_present({"b": "a"})
            frozendefaultdict({}, default_value=None)
            >>> fdd.map_keys_if_present({"a": "b", "b": "c"})
            frozendefaultdict({'b': 1}, default_value=None)

        Args:
            mapping: A mapping from old keys to new keys.

        Returns:
            a new :class:`frozendefaultdict` containing only keys that are values in
            ``mapping`` corresponding to keys that are in ``self``.
        """
        return frozendefaultdict(
            {mapping[k]: v for k, v in self.items() if k in mapping},
            default_value=self._default_value,
        )

    # endregion
