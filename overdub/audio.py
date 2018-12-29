import wave
import audioop
from dataclasses import dataclass
import sounddevice


frame_rate = 44100
frame_size = 4
sample_size = 2

frames_per_block = 1024
bytes_per_block = frame_per_block * frame_size
bytes_per_second = frame_rate * frame_size
seconds_per_byte = 1 / bytes_per_second
seconds_per_block = bytes_per_block * seconds_per_block
blocks_per_second = 1 / seconds_per_block

silence = b'\x00' * bytes_per_block


def add_blocks(blocks):
    """Return a block where with the sum of the samples on all blocks.

    Takes an interable of blocks (byte strings). If no blocks are passed
    a silent block (all zeroes) will be returned.

    Treats None values as silent blocks.
    """
    blocksum = silence

    for block in blocks:
        if block:
            blocksum = audioop.add(blocksum, block, sample_size)

    return blocksum


def get_max_value(block):
    """Return maximum absolute sample value in block.

    The value is normalized to 0..1.
    """
    max_sample = 32768
    return audioop.max(block, sample_size) / max_sample


def block2sec(numblocks):
    return numblocks * seconds_per_block


def sec2block(numsecs):
    return int(round(numsecs * blocks_per_second))


def read_file(filename):
    """Read WAV file and return all data as a list of blocks."""
    blocks = []

    with wave.open(filename, 'r') as infile:

        while True:
            block = infile.readframes(frames_per_block)
            if len(block) == 0:
                break
            elif len(block) < bytes_per_block:
                block += silence[len(block):]

            blocks.append(block)

    return blocks


def write_file(filename, blocks):
    """Write a list of blocks to a WAV file."""
    with wave.open(filename, 'w') as outfile:
        outfile.setnchannels(2)
        outfile.setsampwidth(sample_size)
        outfile.setframerate(frame_rate)

        for block in blocks:
            outfile.writeframes(block)


def stream_to_file(filename):
    outfile = wave.open(filename, 'w')
    outfile.setnchannels(2)
    outfile.setsampwidth(sample_size)
    outfile.setframerate(frame_rate)

    def write(data):
        if data == b'':
            outfile.close()
        else:
            outfile.write(data)

    return write


@dataclass
class CallackInfo:
    stream: sounddevice.RawStream


def set_callback(func):
    def callback_wrapper(inblock, outblock, *_):
        outblock[:] = func(bytes(inblock))
        
    info = CallbackInfo(
        stream=sounddevice.RawStream(
            samplerate=FRAME_RATE,
            channels=2,
            dtype='int16',
            blocksize=frames_per_block,
            callback=callback_wrapper))
    info.stream.start()
    return info


def clear_callback(callback_info):
    callback_info.stream.stop()
