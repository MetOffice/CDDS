# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
from abc import ABCMeta
from enum import EnumMeta


class ABCEnumMeta(ABCMeta, EnumMeta):  # type: ignore

    def __new__(mcls, *args, **kw):
        abstract_enum_cls = super().__new__(mcls, *args, **kw)
        # Only check abstractions if members were defined.
        if abstract_enum_cls._member_map_:
            try:  # Handle existence of undefined abstract methods.
                absmethods = list(abstract_enum_cls.__abstractmethods__)
                if absmethods:
                    missing = ', '.join(str(method) for method in absmethods)
                    plural = 's' if len(absmethods) > 1 else ''
                    raise TypeError(
                        f"cannot instantiate abstract class {abstract_enum_cls.__name__!r}"
                        f" with abstract method{plural} {missing}"
                    )
            except AttributeError:
                pass
        return abstract_enum_cls
