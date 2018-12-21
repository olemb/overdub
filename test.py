from overdub import audio


def callback(input_buffer):
    print('=' * int(audio.get_max_value(input_buffer) * 78))
    return audio.SILENCE


stream = audio.Stream(callback)
stream.start()
input()
stream.stop()
