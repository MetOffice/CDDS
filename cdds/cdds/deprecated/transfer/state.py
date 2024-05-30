# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import abc

"""Represents that states that atomic datasets can occupy in MASS."""

EMBARGOED = "embargoed"
AVAILABLE = "available"
WITHDRAWN = "withdrawn"
SUPERSEDED = "superseded"

KNOWN = [EMBARGOED, AVAILABLE, WITHDRAWN, SUPERSEDED]


def make_state(state):
    """Create an appropriate state object.

    Arguments:
    state -- (str) name of the state to create.
    """
    known = {
        EMBARGOED: Embargoed,
        AVAILABLE: Available,
        WITHDRAWN: Withdrawn,
        SUPERSEDED: Superseded}
    if state in known:
        return known[state]()
    raise ValueError("Unknown state %s" % state)


def known_states():
    """Return list of known states."""
    return KNOWN


class State(object, metaclass=abc.ABCMeta):

    """Abstract base class for state objects.

    Child classes implement the state transitions documented in:
    https://github.com/MetOffice/climate-dds/blob/master/doc/dds_states.pdf

    Abstract methods:
    name -- return name of state
    can_be_put -- return True if datasets can be sent to MASS in this state
    inform -- return True if we inform BADC abou transitions to this state

    Public methods:
    mass_dir -- return MASS sub-dir that represents this state
    can_come_from -- return True if we can move from supplied state to our
    state
    can_move_to -- return True if we can move from our state to supplied state
    """

    def __init__(self):
        self._valid_from_state = []

    @abc.abstractmethod
    def name(self):
        raise NotImplementedError

    @abc.abstractmethod
    def can_be_put(self):
        raise NotImplementedError

    @abc.abstractmethod
    def inform(self):
        raise NotImplementedError

    def mass_dir(self):
        return self.name()

    def can_come_from(self, state):
        for valid in self._valid_from_state:
            if isinstance(state, valid):
                return True
        return False

    def can_move_to(self, state):
        return state.can_come_from(self)

    def __str__(self):
        return self.name()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name() == other.name()
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Embargoed(State):

    def __init__(self):
        # Cannot move to Embargoed from any other state, so leave
        # self._valid_from_state empty.
        super(Embargoed, self).__init__()

    def name(self):
        return EMBARGOED

    def can_be_put(self):
        return True

    def inform(self):
        return False


class Available(State):

    def __init__(self):
        super(Available, self).__init__()
        self._valid_from_state = [Embargoed, Withdrawn]

    def name(self):
        return AVAILABLE

    def can_be_put(self):
        return False

    def inform(self):
        return True


class Withdrawn(State):

    def __init__(self):
        super(Withdrawn, self).__init__()
        self._valid_from_state = [Available, Superseded]

    def name(self):
        return WITHDRAWN

    def can_be_put(self):
        return False

    def inform(self):
        return True


class Superseded(State):

    def __init__(self):
        super(Superseded, self).__init__()
        self._valid_from_state = [Available]

    def name(self):
        return SUPERSEDED

    def can_be_put(self):
        return False

    def inform(self):
        return False
