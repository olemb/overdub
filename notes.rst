Todo:

* add solo button (button 10).
* replace some literals in gamepad.py with constants.
* show time as MM:SS.DD
* play back recording when scrubbing in stopped mode?

https://python-sounddevice.readthedocs.io/en/0.3.7/#sounddevice.Stream

import sounddevice

s = sounddevice.Stream()
print(s.latency)
