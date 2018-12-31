def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    seconds, dec = divmod(seconds, 1)

    minutes = int(minutes)
    seconds = int(seconds)
    decimals = int(dec * 100)

    return f'{minutes:d}:{seconds:02d}:{decimals:02d}'


def make_status_line(deck):
    time = format_time(deck.time)
    end = format_time(deck.end)

    flags = ''

    if deck.solo:
        flags += 's'

    if flags:
        flags = ' ' + flags

    meter = '|' * int(deck.meter * 20)
    meter = '[{}]'.format(meter.ljust(20))

    text = f'{time} / {end} {deck.mode}{flags} {meter}'

    # Screenshot text.
    if False:
        text = {
            'stopped': '0:00:00 / 3:42:37 stopped [||                  ]',
            'playing': '0:20:85 / 3:42:37 playing [|||                 ]',
            'recording':
            '0:11:37 / 3:42:37 recording * [||||||||            ]',
        }[deck.mode]

    return text


SCREENSHOT_TEXT = {
    'stopped': '0:00:00 / 3:42:37 stopped [||                  ]',
    'playing': '0:20:85 / 3:42:37 playing [|||                 ]',
    'recording':
    '0:11:37 / 3:42:37 recording * [||||||||            ]',
}
