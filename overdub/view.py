@dataclass(frozen=True)
class ViewInfo:
    time: float = 0
    end: float = 0
    mode: str = 'stopped'
    meter: float = 0
