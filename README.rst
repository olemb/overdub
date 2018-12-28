Overdub - Simple Multilayered Music Recording
=============================================

.. note:: This is a historical branch that has and undo feature which allows you to undo the last recorded layer.


.. image:: screenshots/playing.png

Overdub allows you to record into an audio buffer with unlimited
overlays and one level of undo.

When you close the program the recording will be written to
``~/Desktop/overdub-out.wav``.

There is experimental support for gamepad controls. See below.

The idea is to have a very simple program that allows me to record
music without looking at a screen.


Status
------

The program is complete and I have started using it, but there are
things that I still need to figure out and improve on:

* the best layout of gamepad controls
* how to ignore key repeat in Tkinter
* should the output file be something else?
* command line arguments (such as ``--fullscreen`` and ``-o/--output-file``)


Requirements
------------

* Python 3
* the ``sounddevice`` package (``pip install sounddevice``)
* runs on Linux or macOS. (Should run on Windows as well but I haven't
  testet it there.)


Display
-------

.. image:: screenshots/playing.png
.. image:: screenshots/recording.png
.. image:: screenshots/stopped.png

The program will start in full screen mode. You can toggle between
fullscreen and windowed mode with the "f" key. I'm thinking of adding
a ``--fullscreen`` flag so you can choose on startup.

The background of the screen changes color to indicate mode: red for
recording, green for playing and black for stopped. This allows you to
tell, even when the screen is well off to the side, which mode you're
in.


Keyboard Controls
-----------------

::

    Enter          toggle recording / playing
    Space Bar      toggle playing / stopped
    Backspace      undo
    Left Arrow     rewind
    Right Arrow    wind
    f              fullscreen

The solo and fast winding buttons found on the gamepad have no
equivalent on the keyboard. This is because I haven't yet found a way
to ignore key repeats in Tkinter.


Gamepad Controls
----------------

Linux only. (Reads from ``/dev/input/js0``.)

Gamepad support is very experimental. I am trying out different button
and joystick layouts so these will probably change a lot. I'm
currently using a LogiTech PlayStation 2 style controller.

The gamepad will be detected and used if present.


License
-------

verdub is released under the terms of the `MIT license
<http://en.wikipedia.org/wiki/MIT_License>`_.


Contact
-------

Ole Martin Bjorndalen - ombdalen@gmail.com
