from dataclasses import dataclass


@dataclass(frozen=True)
class Goto:
    time: float


@dataclass(frozen=True)
class Skip:
    seconds: float


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
class TogglePlay:
    pass


@dataclass(frozen=True)
class ToggleRecord:
    pass

