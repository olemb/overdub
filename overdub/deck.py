import threading
from . import audio

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

        if backend == 'pyaudio':
            # We're opening the output first because we need to feed it some
            # blocks right away.
            self.audiodev = audio.AudioDevice(self._audio_callback)
        else:
            raise ValueError('unknown audio backend {!r}'.format(backend))

        self._sync_event = threading.Event()

    def _sync(self):
        # Todo: timeout.
        self._sync_event.clear()
        self._sync_event.wait()

    def play(self, time=None):
        self.mode = 'playing'
        self.time = time
        self._sync()

    def record(self, time=None):
        if self.mode == 'recording':
            self.mode = 'playing'
        self._sync()

        self.undo_blocks = self.blocks.copy()
        self.time = time
        self.mode = 'recording'
        self._sync()

    def stop(self, time=None):
        self.mode = 'stopped'
        self.time = time
        self._sync()

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

        # Make sure we're not recording anymore.
        self._sync()

        if self.undo_blocks is None:
            return False
        else:
            self.blocks, self.undo_blocks = self.undo_blocks, None

    # Todo: better name:
    def close(self):
        self.stop()
        self.audiodev.close()

    def update_meter(self, block):
        # Todo: scale value by sample rate / block size.
        self.meter = max(self.meter - 0.04, audio.get_max_value(block))

    def _audio_callback(self, inblock):
        self._sync_event.set()

        outblock = audio.SILENCE

        if self.mode != 'stopped':
            block = play_block(self.blocks, self.pos)
            outblock = audio.add_blocks([outblock, block])

        # We need to record after playing back in case the block is
        # recorded at the same position as playback.
        if self.mode == 'recording':
            recpos = self.pos - self.audiodev.play_ahead
            record_block(self.blocks, recpos, inblock)

        if self.mode != 'stopped':
            self.pos += 1

        self.update_meter(audio.add_blocks([inblock, outblock]))
        
        return outblock
