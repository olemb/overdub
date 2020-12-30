from dataclasses import dataclass


@dataclass(frozen=True)
class Status:
    time: float = 0
    end: float = 0
    mode: str = 'stopped'
    solo: bool = False
    meter: float = 0
