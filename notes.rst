Todo:

* show time as MM:SS.DD
* play back recording when scrubbing in stopped mode?

https://python-sounddevice.readthedocs.io/en/0.3.7/#sounddevice.Stream

import sounddevice

s = sounddevice.Stream()
print(s.latency)
