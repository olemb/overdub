import os
import struct
from dataclasses import dataclass


class GamepadEvent:
    def is_axis(self, axis=None):
        if self.type != 'axis':
            return False
        elif axis is not None and self.axis != axis:
            return False
        else:
            return True

    def is_button(self, button=None):
        if self.type != 'button':
            return False
        elif button is not None and self.button != button:
            return False
        else:
            return True

    def is_button_press(self, button=None):
        return self.is_button(button) and self.pressed


@dataclass(frozen=True)
class ButtonEvent(GamepadEvent):
    type: str
    button: int
    pressed: bool
    is_init: bool
    timestamp: int


@dataclass(frozen=True)
class AxisEvent(GamepadEvent):
    type: str
    axis: int
    value: float
    raw_value: int
    is_init: bool
    timestamp: int


def normalize_value(value):
    """Normalize value to -1..1."""
    return float(value) / 0x7FFF


def parse_event(data):
    timestamp, raw_value, event_type, number = struct.unpack('IhBB', data)
    is_init = bool(event_type & 0x80)

    type_str = {
        1: 'button',
        2: 'axis',
    }[event_type & 0x7F]

    if type_str == 'button':
        return ButtonEvent(
            type=type_str,
            button=number,
            pressed=bool(raw_value),
            is_init=is_init,
            timestamp=timestamp,
        )
    else:
        return AxisEvent(
            type=type_str,
            axis=number,
            value=normalize_value(raw_value),
            raw_value=raw_value,
            is_init=is_init,
            timestamp=timestamp,
        )


def read_event(device):
    event_size = 8
    return parse_event(device.read(event_size))


def gamepad_exists(number):
    return os.path.exists(f'/dev/input/js{number}')


def list_gamepads():
    return [i for i in range(16) if gamepad_exists(i)]


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
