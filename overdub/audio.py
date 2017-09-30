import wave
import audioop
import sounddevice

FRAME_RATE = 44100
SAMPLE_WIDTH = 2
NUM_CHANNELS = 2
FRAME_SIZE = SAMPLE_WIDTH * NUM_CHANNELS

FRAMES_PER_BLOCK = 1024
BYTES_PER_BLOCK = FRAMES_PER_BLOCK * FRAME_SIZE

SILENCE = b'\x00' * BYTES_PER_BLOCK

BYTES_PER_SECOND = FRAME_RATE * FRAME_SIZE
SECONDS_PER_BYTE = 1 / BYTES_PER_SECOND
SECONDS_PER_BLOCK = BYTES_PER_BLOCK * SECONDS_PER_BYTE
BLOCKS_PER_SECOND = 1 / SECONDS_PER_BLOCK


def add_blocks(blocks):
    """Return a block where with the sum of the samples on all blocks.

    Takes an interable of blocks (byte strings). If no blocks are passed
    a silent block (all zeroes) will be returned.

    Treats None values as silent blocks.
    """
    blocksum = SILENCE

    for block in blocks:
        if block:
            blocksum = audioop.add(blocksum, block, SAMPLE_WIDTH)

    return blocksum


def get_max_value(block):
    """Return maximum absolute sample value in block.

    The value is normalized to 0..1.
    """
    max_sample = 32768
    return audioop.max(block, SAMPLE_WIDTH) / max_sample


def block2sec(numblocks):
    return numblocks * SECONDS_PER_BLOCK


def sec2block(numsecs):
    return int(round(numsecs * BLOCKS_PER_SECOND))


def load(filename):
    """Read WAV file and return all data as a list of blocks."""
    blocks = []

    with wave.open(filename, 'r') as infile:

        while True:
            block = infile.readframes(FRAMES_PER_BLOCK)
            if len(block) == 0:
                break
            elif len(block) < BYTES_PER_BLOCK:
                block += SILENCE[len(block):]

            blocks.append(block)

    return blocks


def save(filename, blocks):
    """Write a list of blocks to a WAV file."""
    with wave.open(filename, 'w') as outfile:
        outfile.setnchannels(NUM_CHANNELS)
        outfile.setsampwidth(SAMPLE_WIDTH)
        outfile.setframerate(FRAME_RATE)

        for block in blocks:
            outfile.writeframes(block)


class Stream:
    def __init__(self, callback):
        def callback_wrapper(inblock, outblock, *_):
            outblock[:] = callback(inblock)

        self.stream = sounddevice.RawStream(
            channels=2,
            dtype='int16',
            blocksize=FRAMES_PER_BLOCK,
            callback=callback_wrapper)

        self.latency = sum(self.stream.latency)
        self.play_ahead = int(round(self.latency * BLOCKS_PER_SECOND))

    def start(self):
        self.stream.start()

    def stop(self):
        self.stream.stop()
