import queue
from threading import Event
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


class Task:
    def __init__(self, func):
        self.func = func
        self.return_value = None
        self.event = Event()


class CommandQueue:
    def __init__(self):
        self.q = queue.Queue()

    def put(self, func):
        task = Task(func)
        self.q.put(task)
        task.event.wait()
        return task.return_value

    def handle(self):
        while True:
            try:
                task = self.q.get_nowait()
            except queue.Empty:
                return
            else:
                try:
                    task.return_value = task.func()
                finally:
                    task.event.set()


class Deck:
    def __init__(self):
        self.pos = 0
        self.mode = 'stopped'
        self.solo = False
        self.scrub = 0.0
        self.meter = 0

        self.blocks = []

        self._stream = audio.Stream(self._audio_callback)
        self._stream.start()

        self._command_queue = CommandQueue()
        self.in_callback = self._command_queue.put

    def close(self):
        self._stream.stop()

    def load(self, filename):
        self.blocks = audio.load(filename)

    def save(self, filename):
        audio.save(filename, self.blocks)

    @property
    def status(self):
        return Status(
            time=audio.block2sec(self.pos),
            end=audio.block2sec(len(self.blocks)),
            mode=self.mode,
            solo=self.solo,
            meter=self.meter,
        )

    def _update_meter(self, block):
        # TODO: scale value by sample rate / block size.
        self.meter = max(self.meter - 0.04, audio.get_max_value(block))

    def goto(self, seconds):
        @self.in_callback
        def _():
            self.pos = max(0, audio.sec2block(seconds))
            if self.mode == 'recording':
                self.mode = 'playing'

    def skip(self, seconds):
        @self.in_callback
        def _():
            self.pos = max(0, self.pos + audio.sec2block(seconds))
            if self.mode == 'recording':
                self.mode = 'playing'

    def scrub(self, speed):
        @self.in_callback
        def _():
            if speed != 0 and self.mode == 'recording':
                self.mode = 'playing'
            self.scrub = speed

    def toggle_play(self):
        @self.in_callback
        def _():
            self.mode = {
                'stopped': 'playing',
                'playing': 'stopped',
                'recording': 'stopped',
            }[self.mode]

    def toggle_record(self):
        @self.in_callback
        def _():
            self.mode = {
                'stopped': 'recording',
                'playing': 'recording',
                'recording': 'playing',
            }[self.mode]

    def record(self):
        @self.in_callback
        def _():
            self.mode = 'recording'

    def play(self):
        @self.in_callback
        def _():
            self.mode = 'playing'

    def stop(self):
        @self.in_callback
        def _():
            self.mode = 'stopped'

    def punch_in(self):
        @self.in_callback
        def _():
            self.mode = 'recording'

    def punch_out(self):
        @self.in_callback
        def _():
            if self.mode == 'recording':
                self.mode = 'playing'

    def _audio_callback(self, inblock):
        self._command_queue.handle()

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
