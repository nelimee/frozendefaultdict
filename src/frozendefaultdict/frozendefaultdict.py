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
    pass


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
        return len(self._dict)

    @override
    def __iter__(self) -> Iterator[K]:
        return iter(self._dict)

    @override
    def __contains__(self, key: object) -> bool:
        return self._dict.__contains__(key)

    @override
    def __getitem__(self, key: K) -> V_co:
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
        return hash((frozenset(self.items()), self._default_value))

    def __eq__(self, other: object) -> bool:
        """Check equality based on stored items *and* default value.

        Two instances are equal iff they contain the same key-value pairs and share the
        same ``default_value``. Comparison with non-:class:`frozendefaultdict` objects
        always returns ``False``.
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
        """
        return self

    def __deepcopy__(self, memo: dict[int, Any]) -> frozendefaultdict[K, V_co]:
        """Return a deep-copy of ``self``."""
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
        """Return ``True`` if a default value was provided."""
        return not isinstance(self._default_value, _NoDefaultProvided)

    @property
    def default_value(self) -> V_co:
        """Return the default value provided at instance construction or raise if none
        was provided.

        Raises:
            NoDefaultValueProvidedError: if the ``default_value`` argument was not
                provided at the creation of ``self``.
        """
        if isinstance(self._default_value, _NoDefaultProvided):
            raise NoDefaultValueProvidedError()
        return self._default_value

    def map_keys(self, func: Callable[[K], K]) -> frozendefaultdict[K, V_co]:
        """Return a new instance with every key replaced by ``func(key)``.

        Values and the default value stay unchanged.

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
