import struct
from dataclasses import dataclass


@dataclass(frozen=True)
class GamepadEvent:
    type: str       # 'button' or 'axis'
    number: int     # Which button or axis.
    value: float    # Normalized value.
    is_init: bool   # Is initialize event.
    raw_value: int  # Value.
    timestamp: int

    def is_axis(self, number=None):
        if self.type != 'axis':
            return False
        elif number is not None and self.number != number:
            return False
        else:
            return True

    def is_button(self, number=None):
        if self.type != 'button':
            return False
        elif number is not None and self.number != number:
            return False
        else:
            return True


def normalize_value(value):
    """Normalize value to -1..1."""
    return float(value) / 0x7fff


def parse_event(data):
    timestamp, value, event_type, number = struct.unpack('IhBB', data)
    
    event_type_str = {1: 'button', 2: 'axis'}[event_type & 0x7f]

    if event_type_str == 'axis':
        normalized_value = normalize_value(value)
    else:
        normalized_value = bool(value)

    return GamepadEvent(is_init=bool(event_type & 0x80),
                        type=event_type_str,
                        number=number,
                        value=normalized_value,
                        raw_value=value,
                        timestamp=timestamp)


def read_event(device):
    event_size = 8
    return parse_event(device.read(event_size))


def iter_gamepad(number, include_init=False):
    if not (isinstance(number, int) and number >= 0):
        raise ValueError('gamepad number must be positive integer')

    with open(f'/dev/input/js{number}', 'rb') as infile:
        while True:
            event = read_event(infile)
            if event.is_init:
                if include_init:
                    yield event
            else:
                yield event


def example1():
    """Print axis 0 events."""
    for event in iter_gamepad(0):
        if ev.is_axis(0):
            print(ev.value)
