from functools import partial
from typing import Any, ClassVar

import pytest
from _pytest.fixtures import FixtureRequest


def _inject(cls: ClassVar, names: Any) -> ClassVar:  # type:ignore
    @pytest.fixture(autouse=True)
    def auto_injector_fixture(self, request: FixtureRequest) -> None:  # type:ignore
        """
        Inject external resources as fixtures
        """
        for name in names:
            setattr(self, name, request.getfixturevalue(name))

    cls.__auto_injector_fixture = auto_injector_fixture
    return cls


def auto_inject_fixtures(*names: Any) -> partial:
    """
    Decorator to inject fixtures
    :param names: A list of fixtures to inject
    :return: Returns a partial
    """
    return partial(_inject, names=names)
