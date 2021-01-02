import queue
import functools
from . import audio
from .status import Status


def play_block(blocks, pos):
    if blocks is None:
        return audio.silence
    if 0 <= pos < len(blocks):
        return blocks[pos]
    else:
        return audio.silence


def record_block(blocks, pos, block):
    if pos < 0:
        return
    elif pos < len(blocks):
        blocks[pos] = audio.sum_blocks([blocks[pos], block])
    elif pos == len(blocks):
        blocks.append(block)
    else:
        gap = pos - len(blocks)
        blocks.extend([audio.silence] * gap)
        blocks.append(block)


def in_callback(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        def func():
            return method(self, *args, **kwargs)

        return self._command_queue.put(func)

    return wrapper


class Deck:
    def __init__(self):
        self.pos = 0
        self.mode = 'stopped'
        self.solo = False
        self.scrub = 0.0
        self.meter = 0

        self.blocks = []

        self._stream = audio.Stream(self._audio_callback)

        self._command_queue = queue.Queue()

    def start_stream(self):
        self._stream.start()

    def stop_stream(self):
        self._stream.stop()

    def load(self, filename):
        self.blocks = audio.load(filename)

    def save(self, filename):
        audio.save(filename, self.blocks)

    def get_status(self):
        return Status(
            time=audio.block2sec(self.pos),
            end=audio.block2sec(len(self.blocks)),
            mode=self.mode,
            solo=self.solo,
            meter=self.meter,
        )

    @in_callback
    def goto(self, seconds):
        self.pos = max(0, audio.sec2block(seconds))
        if self.mode == 'recording':
            self.mode = 'playing'

    @in_callback
    def skip(self, seconds):
        self.pos = max(0, self.pos + audio.sec2block(seconds))
        if self.mode == 'recording':
            self.mode = 'playing'

    @in_callback
    def scrub(self, speed):
        if speed != 0 and self.mode == 'recording':
            self.mode = 'playing'
        self.scrub = speed

    @in_callback
    def toggle_play(self):
        self.mode = {
            'stopped': 'playing',
            'playing': 'stopped',
            'recording': 'stopped',
        }[self.mode]

    @in_callback
    def toggle_record(self):
        self.mode = {
            'stopped': 'recording',
            'playing': 'recording',
            'recording': 'playing',
        }[self.mode]

    @in_callback
    def record(self):
        self.mode = 'recording'

    @in_callback
    def play(self):
        self.mode = 'playing'

    @in_callback
    def stop(self):
        self.mode = 'stopped'

    @in_callback
    def punch_in(self):
        self.mode = 'recording'

    @in_callback
    def punch_out(self):
        if self.mode == 'recording':
            self.mode = 'playing'

    def _update_meter(self, block):
        # TODO: scale value by sample rate / block size.
        self.meter = max(self.meter - 0.04, audio.get_max_value(block))

    def _handle_commands(self):
        while True:
            try:
                func = self._command_queue.get_nowait()
            except queue.Empty:
                return
            else:
                func()

    def _audio_callback(self, inblock):
        self._handle_commands()

        if self.scrub != 0:
            self.pos += int(round(self.scrub))
            if self.pos < 0:
                self.pos = 0

        if (self.mode != 'stopped' or self.scrub) and not self.solo:
            outblock = play_block(self.blocks, self.pos)
        else:
            outblock = audio.silence

        # We need to record after playing back in case the block is
        # recorded at the same position as playback.
        if self.mode == 'recording':
            recpos = self.pos - self._stream.play_ahead
            record_block(self.blocks, recpos, inblock)

        if self.mode != 'stopped':
            self.pos += 1

        if self.solo:
            self._update_meter(inblock)
        else:
            self._update_meter(audio.sum_blocks([inblock, outblock]))

        return outblock
