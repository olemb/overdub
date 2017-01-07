import time
from overdub import audio


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
    def __init__(self, blocks=None):
        self.pos = 0
        self.mode = 'stopped'

        if blocks is None:
            self.blocks = []
        else:
            self.blocks = blocks

        # We're opening the output first because we need to feed it some
        # blocks right away.
        self.audio_out = audio.AudioDevice('w')
        self.audio_in = audio.AudioDevice('r')

        self.blocklag = 3

    # Todo: better name:
    def close(self):
        self.audio_in.close()
        self.audio_out.close()

    # Todo: better name:
    def handle_block(self):
        inblock = self.audio_in.read_block()
        outblock = audio.SILENCE

        if self.mode != 'stopped':
            block = play_block(self.blocks, self.pos)
            outblock = audio.add_blocks([outblock, block])

        # We need to record after playing back in case the block is
        # recorded at the same position as playback.
        if self.mode == 'recording':
            record_block(self.blocks, self.pos - self.blocklag, inblock)

        if self.mode != 'stoped':
            self.pos += 1

        self.audio_out.write_block(outblock)


def test_blocklag():
    def do_blocks(deck, n):
        for _ in range(n):
            deck.handle_block()


    deck = Deck()


    while True:
        print('Rewind!')
        deck.pos = 0
        deck.mode = 'recording'
        do_blocks(deck, 43)


test_blocklag()
