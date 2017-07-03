Todo:

* what happened to blocklag after deck refactoring?
* update audio.py with code from Canvas.
* make audio device I/O.
* get latency from audio device object.

https://python-sounddevice.readthedocs.io/en/0.3.7/#sounddevice.Stream

import sounddevice

s = sounddevice.Stream()
print(s.latency)
