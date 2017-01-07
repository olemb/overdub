#!/usr/bin/env python3
"""
https://gist.github.com/ignacysokolowski/3973029#file-pulse_simple_play-py
https://freedesktop.org/software/pulseaudio/doxygen/simple_8h.html
https://freedesktop.org/software/pulseaudio/doxygen/def_8h.html
"""
import ctypes
import wave
import sys
from . import audio

pa = ctypes.cdll.LoadLibrary('libpulse-simple.so.0')

PA_STREAM_PLAYBACK = 1
PA_STREAM_RECORD = 2
PA_SAMPLE_S16LE = 3
BUFSIZE = 1024


class struct_pa_sample_spec(ctypes.Structure):
    __slots__ = [
        'format',
        'rate',
        'channels',
    ]

struct_pa_sample_spec._fields_ = [
    ('format', ctypes.c_int),
    ('rate', ctypes.c_uint32),
    ('channels', ctypes.c_uint8),
]
pa_sample_spec = struct_pa_sample_spec  # /usr/include/pulse/sample.h:174



class AudioDevice:
    def __init__(self, mode):
        self.mode = mode
        self.closed = False

        self._error = ctypes.c_int(0)

        # Defining sample format.
        spec = struct_pa_sample_spec()
        spec.rate = audio.FRAME_RATE
        spec.channels = audio.NUM_CHANNELS
        spec.format = PA_SAMPLE_S16LE

        if mode == 'r':
            stream_direction = PA_STREAM_RECORD
        elif mode == 'w':
            stream_direction = PA_STREAM_PLAYBACK
        else:
            raise ValuError('invalid stream mode {!r}'.format(mode))

        # Creating a new playback stream.
        self.stream = pa.pa_simple_new(
            None,  # Default server.
            'appname',  # Application's name.
            stream_direction,
            None,  # Default device.
            'playback',  # Stream's description.
            ctypes.byref(spec),  # Sample format.
            None,  # Default channel map.
            None,  # Default buffering attributes.
            ctypes.byref(self._error)  # Ignore error code.
        )

        if not self.stream:
            raise Exception('Could not create pulse audio stream: {0}!'.format(
                pa.strerror(ctypes.byref(self._error))))

    def _read(self, numframes):
        # Frame size is 4 bytes.
        bufsize = numframes * 4

        buf = ctypes.create_string_buffer(b' ' * bufsize)

        if pa.pa_simple_read(self.stream, ctypes.byref(buf), bufsize, self._error):
            raise Exception('Could not read from stream')

        # The slice is there to remove string termination.
        data = bytes(bytearray(buf)[:-1])

        # Todo: free buffer?

        return data

    def _write(self, data):
        if len(data) == 0:
            return

        if pa.pa_simple_write(self.stream, data, len(data), self._error):
            raise Exception('Could not write to stream')

    def read_block(self):
        return self._read(audio.FRAMES_PER_BLOCK)

    def write_block(self, block):
        self._write(block)

    @property
    def latency(self):
        # Getting latency.
        latency = pa.pa_simple_get_latency(self.stream, self._error)
        if latency == -1:
            raise Exception('Getting latency failed!')
        return latency

    def close(self):
        if not self.closed:
            if self.mode == 'w':
                if pa.pa_simple_drain(self.stream, self._error):
                    raise Exception('Could not simple drain!')

            pa.pa_simple_free(self.stream)

            self.closed = True
