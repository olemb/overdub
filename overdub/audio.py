"""
Todo:

* fade in first playback frame and fade out last frame (to make
  skipping sound smoother)
"""

import sys
if sys.version_info.major < 3:
    sys.exit('Requires Python 3')

import wave
import atexit
import audioop
import pyaudio
from pyaudio import PyAudio

pa = None

BYTES_PER_BLOCK = 4096

FRAME_RATE = 44100
SAMPLE_WIDTH = 2
NUM_CHANNELS = 2
FRAME_SIZE = SAMPLE_WIDTH * NUM_CHANNELS
SILENCE = b'\x00' * BYTES_PER_BLOCK

# Todo: not sure if these are correct.
FRAMES_PER_BLOCK = int(BYTES_PER_BLOCK / FRAME_SIZE)

BYTES_PER_SECOND = FRAME_RATE * FRAME_SIZE
SECONDS_PER_BYTE = 1 / BYTES_PER_SECOND
SECONDS_PER_BLOCK = BYTES_PER_BLOCK * SECONDS_PER_BYTE
BLOCKS_PER_SECOND = 1 / SECONDS_PER_BLOCK

PA_AUDIO_FORMAT = dict(format=pyaudio.paInt16,
                       channels=NUM_CHANNELS,
                       rate=FRAME_RATE,
                       frames_per_buffer=FRAMES_PER_BLOCK)

def _pa_init():
    global pa
    if pa is None:
        pa = PyAudio()
        atexit.register(_pa_terminate)


def _pa_terminate():
    global pa
    if pa:
        pa.terminate()
        pa = None


def terminate():
    if pa is not None:
        pa.terminate()


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


def block2sec(numblocks):
    return numblocks * SECONDS_PER_BLOCK


def sec2block(numsecs):
    return round(numsecs * BLOCKS_PER_SECOND)


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


class AudioDevice:
    def __init__(self, mode):
        _pa_init()
        self.mode = mode
        self.closed = False

        if mode == 'r':
            self.dev = pa.open(input=True, **PA_AUDIO_FORMAT)
        elif mode == 'w':
            self.dev = pa.open(output=True, **PA_AUDIO_FORMAT)
            for _ in range(4):
                self.write_block(SILENCE)
        else:
            raise ValueError('unknown mode {!r}'.format(mode))

    def read_block(self):
        if self.closed:
            raise ValueError('audio device is closed')

        if self.mode != 'r':
            raise ValueError('audio device is write only')

        return self.dev.read(FRAMES_PER_BLOCK)

    def write_block(self, block):
        if self.closed:
            raise ValueError('audio device is closed')

        if self.mode != 'w':
            raise ValueError('audio device is read only')

        if not self.closed:
            self.dev.write(block)

    def close(self):
        if not self.closed:
            self.dev.close()

    def __enter__(self):
        return self

    def __exit__(self, *_, **__):
        self.close()
        return False
