from dataclasses import dataclass


@dataclass(frozen=True)
class Goto:
    time: float


@dataclass(frozen=True)
class Skip:
    seconds: float


@dataclass(frozen=True)
class Scrub:
    speed: float


@dataclass(frozen=True)
class Record:
    pass


@dataclass(frozen=True)
class Play:
    pass


@dataclass(frozen=True)
class Stop:
    pass


@dataclass(frozen=True)
class ToggleRecord:
    pass


@dataclass(frozen=True)
class TogglePlay:
    pass


@dataclass(frozen=True)
class PunchIn:
    pass


@dataclass(frozen=True)
class PunchOut:
    pass


__all__ = ['Goto', 'Skip', 'Scrub', 'Record', 'Play', 'Stop',
           'ToggleRecord', 'TogglePlay', 'PunchIn', 'PunchOut']
