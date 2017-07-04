Todo:

* add solo button (button 10).
* replace some literals in joystick.py with constants.
* show time as MM:SS.DD
* change joystick event format? (type, code (instead of number), value)
* play back recording when scrubbing in stopped mode?

https://python-sounddevice.readthedocs.io/en/0.3.7/#sounddevice.Stream

import sounddevice

s = sounddevice.Stream()
print(s.latency)
