import os


def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    seconds, dec = divmod(seconds, 1)

    minutes = int(minutes)
    seconds = int(seconds)
    decimals = int(dec * 100)

    return f'{minutes:d}:{seconds:02d}:{decimals:02d}'


def format_status(status):
    time = format_time(status.time)
    end = format_time(status.end)

    flags = ''

    if status.solo:
        flags += 's'

    if flags:
        flags = ' ' + flags

    meter = ('|' * int(status.meter * 20)).ljust(20)

    return f'{time} / {end} {status.mode}{flags} [{meter}]'


def _fake_status_for_screenshot(status):
    """Return a fake status line for screenshots."""
    return {
        'stopped': '0:00:00 / 3:42:37 stopped [||                  ]',
        'playing': '0:20:85 / 3:42:37 playing [|||                 ]',
        'recording':
        '0:11:37 / 3:42:37 recording * [||||||||            ]',
    }[status.mode]


if os.environ.get('OVERDUB_SCREENSHOT'):
    format_status = _fake_status_for_screenshot  # noqa: F881
