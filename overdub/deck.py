from . import audio
from . import pulse

def play_block(blocks, pos):
    if 0 <= pos < len(blocks):
        return blocks[pos]
    else:
        return audio.SILENCE


def record_block(blocks, pos, block):
    if pos < 0:
        return
    elif pos < len(blocks):
        blocks[pos] = audio.add_blocks([blocks[pos], block])
    elif pos == len(blocks):
        blocks.append(block)
    else:
        gap = pos - len(blocks)
        blocks.extend([audio.SILENCE] * gap)
        blocks.append(block)


class Deck:
    def __init__(self, blocks=None, backend='pyaudio'):
        self.pos = 0
        self.mode = 'stopped'

        self.meter = 0

        if blocks is None:
            self.blocks = []
        else:
            self.blocks = blocks

        self.undo_blocks = None

        if backend == 'pulse':
            self.audio_out = pulse.AudioDevice('w')
            self.audio_in = pulse.AudioDevice('r')

            # self.blocklag = 18  # PulseAudio (laptop)
            self.blocklag = 7  # PulseAudio (SH-201)

        elif backend == 'pyaudio':
            # We're opening the output first because we need to feed it some
            # blocks right away.
            self.audio = audio.AudioDevice()
            self.audio_out = self.audio
            self.audio_in = self.audio
            self.blocklag = self.audio.blocklag

        else:
            raise ValueError('unknown audio backend {!r}'.format(backend))

    def record(self, time=None):
        self.mode = 'stopped'
        self.time = time

    def play(self, time=None):
        self.mode = 'playing'
        self.time = time

    def record(self, time=None):
        self.undo_blocks = self.blocks.copy()
        self.mode = 'recording'
        self.time = time

    def stop(self, time=None):
        self.mode = 'stopped'
        self.time = time

    def toggle_play(self):
        if self.mode == 'stopped':
            self.play()
        else:
            self.stop()

    def toggle_record(self):
        if self.mode == 'recording':
            self.play()
        else:
            self.record()

    @property
    def time(self):
        return self.pos * audio.SECONDS_PER_BLOCK

    @time.setter
    def time(self, time):
        # This is used for keyword arguments where the default is None.
        if time is None:
            return

        self.pos = int(round(time * audio.BLOCKS_PER_SECOND))

        if self.pos < 0:
            self.pos = 0

    @property
    def end(self):
        return len(self.blocks) * audio.SECONDS_PER_BLOCK
 
    def skip(self, time):
        if time == 0:
            return

        if self.mode == 'recording':
            self.mode = 'playing'

        self.time += time

    def undo(self):
        """Restores from undo buffer.

        Returns True if restore was done or False if the undo buffer
        was empty.
        """
        if self.mode == 'recording':
            self.mode = 'playing'

        if self.undo_blocks is None:
            return False
        else:
            self.blocks, self.undo_blocks = self.undo_blocks, None

    # Todo: better name:
    def close(self):
        self.audio_in.close()
        self.audio_out.close()

    def update_meter(self, block):
        # Todo: scale value by sample rate / block size.
        self.meter = max(self.meter - 0.04, audio.get_max_value(block))

    def update(self):
        inblock = self.audio_in.read_block()
        outblock = audio.SILENCE

        # print(self.audio_in.latency, self.audio_out.latency)

        if self.mode != 'stopped':
            block = play_block(self.blocks, self.pos)
            outblock = audio.add_blocks([outblock, block])

        # We need to record after playing back in case the block is
        # recorded at the same position as playback.
        self.blocklag = 5
        if self.mode == 'recording':
            record_block(self.blocks, self.pos - self.blocklag, inblock)

        if self.mode != 'stopped':
            self.pos += 1

        self.update_meter(audio.add_blocks([inblock, outblock]))

        self.audio_out.write_block(outblock)
