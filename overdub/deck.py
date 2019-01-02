import queue
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
        blocks[pos] = audio.add_blocks([blocks[pos], block])
    elif pos == len(blocks):
        blocks.append(block)
    else:
        gap = pos - len(blocks)
        blocks.extend([audio.silence] * gap)
        blocks.append(block)


class CommandQueue:
    """What's going on here is really subtle and need to be documented at
    some point.

    Short version:

    queue.do(Skip(1))
    queue.do(Goto(0), Record())  # Atomic. Guaranteed to start recording at 0.

    The audio callback will execute all pending commands before it
    starts processing audio. Thus the operation above is guaranteed to
    be atomic.
    """
    def __init__(self):
        self.q = queue.Queue()
    
    def do(self, *commands):
        self.q.put(commands)

    def __iter__(self):
        while True:
            try:
                yield from self.q.get_nowait()
            except queue.Empty:
                return


class Deck:
    def __init__(self, blocks=None):
        self.pos = 0
        self.mode = 'stopped'
        self.solo = False
        self.scrub = False
        self.meter = 0

        if blocks is None:
            self.blocks = []
        else:
            self.blocks = blocks

        self._command_queue = CommandQueue()
        self.do = self._command_queue.do
        self._stream_info = audio.start_stream(self._audio_callback)

    def close(self):
        audio.stop_stream(self._stream_info)

    def get_status(self):
        return Status(time=audio.block2sec(self.pos),
                      end=audio.block2sec(len(self.blocks)),
                      mode=self.mode,
                      solo=self.solo,
                      meter=self.meter)

    def update_meter(self, block):
        # TODO: scale value by sample rate / block size.
        self.meter = max(self.meter - 0.04, audio.get_max_value(block))

    def _handle_commands(self):
        for cmd in self._command_queue:

            # TODO: this is kind of awkward.
            name = cmd.__class__.__name__
            
            if name == 'Goto':
                self.pos = max(0, audio.sec2block(cmd.time))
                if self.mode == 'recording':
                    self.mode = 'playing'

            elif name == 'Skip':
                self.pos = max(0, self.pos + audio.sec2block(cmd.seconds))
                if self.mode == 'recording':
                    self.mode = 'playing'

            elif name == 'TogglePlay':
                self.mode = {'stopped': 'playing',
                             'playing': 'stopped',
                             'recording': 'playing'}[self.mode]

            elif name == 'ToggleRecord':
                self.mode = {'stopped': 'recording',
                             'playing': 'recording',
                             'recording': 'playing'}[self.mode]

            elif name == 'Record':
                self.mode = 'record'

            elif name == 'Play':
                self.mode = 'playing'

            elif name == 'Stop':
                self.mode = 'stopped'
                
    def _audio_callback(self, inblock):
        self._handle_commands()

        if (self.mode != 'stopped' or self.scrub) and not self.solo:
            outblock = play_block(self.blocks, self.pos)
        else:
            outblock = audio.silence

        # We need to record after playing back in case the block is
        # recorded at the same position as playback.
        if self.mode == 'recording':
            recpos = self.pos - self._stream_info.play_ahead
            record_block(self.blocks, recpos, inblock)

        if self.mode != 'stopped':
            self.pos += 1

        if self.solo:
            self.update_meter(inblock)
        else:
            self.update_meter(audio.add_blocks([inblock, outblock]))

        return outblock
