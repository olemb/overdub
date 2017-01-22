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

        if blocks is None:
            self.blocks = []
        else:
            self.blocks = blocks

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

    # Todo: better name:
    def close(self):
        self.audio_in.close()
        self.audio_out.close()

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

        self.audio_out.write_block(outblock)
