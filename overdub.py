#!/usr/bin/env python3
"""
http://www.ittc.ku.edu/~niehaus/classes/448-s04/448-standard/simple_gui_examples/index.html
http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
"""
import os
import sys
import time
import tkinter as tk
import tkinter.font
from overdub import audio
from overdub.deck import Deck
from overdub.gamepad import Gamepad


def get_font(size):
    return tkinter.font.Font(family='Courier', size=size)


def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    seconds, dec = divmod(seconds, 1)

    minutes = int(minutes)
    seconds = int(seconds)
    dec = int(dec * 100)

    return '{:d}:{:02d}:{:02d}'.format(minutes, seconds, dec)


class GUI:
    def __init__(self, deck, filename, fullscreen=True):
        self.deck = deck
        self.filename = filename
        self.fullscreen = fullscreen

        self.gamepad = Gamepad(optional=True)

        self.player = None
        self.recorder = None

        self.window = tk.Tk()
        self.window.title('Overdub')

        self.window.protocol("WM_DELETE_WINDOW", self.quit)

        self.statusbar = tk.StringVar()
        label = tk.Label(textvariable=self.statusbar)
        label['font'] = get_font(size=30)
        label['foreground'] = 'white'
        label.pack(side=tk.TOP, padx=10, pady=10)
        self.statusbar_label = label

        label = tk.Label(text=self.filename)
        label['font'] = get_font(size=15)
        label['foreground'] = 'white'
        label.pack(side=tk.TOP, padx=10, pady=10)
        self.filename_label = label

        def wrap(func):
            """Wrap event handler in a function that ignores event."""
            return lambda *_: func()

        self.window.bind('<KeyPress-Return>', wrap(self.deck.toggle_record))
        self.window.bind('<KeyPress-space>', wrap(self.deck.toggle_play))
        self.window.bind('<KeyPress-BackSpace>', wrap(self.deck.undo))

        self.window.bind('<ButtonPress-2>', wrap(self.deck.toggle_record))

        self.skipdist = 0

        def skip_less(_):
            self.skipdist -= 1
            
        def skip_more(_):
            self.skipdist += 1

        self.gamepad_skipdist = 0

        # We can't use KeyPress/KeyRelease because of key repeat.
        self.window.bind('<ButtonPress-1>', skip_less)
        self.window.bind('<ButtonRelease-1>', skip_more)

        self.window.bind('<ButtonPress-3>', skip_more)
        self.window.bind('<ButtonRelease-3>', skip_less)

        self.window.bind('<KeyPress-Left>', skip_less)
        self.window.bind('<KeyRelease-Left>', skip_more)

        self.window.bind('<KeyPress-Right>', skip_more)
        self.window.bind('<KeyRelease-Right>', skip_less)

        self.window.bind('<KeyPress-f>', wrap(self.toggle_fullscreen))

        self.window.attributes("-fullscreen", self.fullscreen)

        self.update()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.window.attributes("-fullscreen", self.fullscreen)

    def handle_gamepad(self):
        for event in self.gamepad.events:
            # Right gamepad.
            if (event['type'], event['code']) == ('axis', 2):
                value = event['value']

                # Sometimes the gamepad doesn't go all the way back to 0.0.
                if abs(value) < 0.05:
                    value = 0

                if value >= 0:
                    sign = 1
                else:
                    sign = -1

                value = (abs(value) ** 4) * 4 * sign
                
                self.gamepad_skipdist = value
                self.deck.scrub = bool(value)

            elif event['type'] == 'button':
                # Add 1 because buttons are numbered 1-10 on the gamepad.
                button = event['code'] + 1

                if button == 10:
                    self.deck.solo = bool(event['value'])

                elif event['value'] is True:
                    if button == 1:
                        self.deck.record()
                    elif button == 2:
                        self.deck.stop()
                    elif button == 3:
                        self.deck.play()
                    elif button == 4:
                        self.deck.undo()

    def update(self):
        # self.window.update()
        self.handle_gamepad()
        self.deck.skip(self.skipdist)
        self.deck.skip(self.gamepad_skipdist)
        self.update_display()

        background = {'recording': '#a00',  # Red
                      'playing': '#050',  # Green
                      'stopped': 'black'}[self.deck.mode]

        for widget in [self.window, self.statusbar_label, self.filename_label]:
            widget['background'] = background

        self.window.after(50, self.update)

    def mainloop(self):
        try:
            self.window.mainloop()
        except KeyboardInterrupt:
            return
        finally:
            pass

    def update_display(self):
        flags = ''

        if self.deck.undo_blocks is not None:
            flags += '*'

        if self.deck.solo:
            flags += 's'

        if flags:
            flags = ' ' + flags

        meter = '|' * int(self.deck.meter * 20)
        meter = '[{}]'.format(meter.ljust(20))

        text = '{} / {} {}{} {}'.format(format_time(self.deck.time),
                                        format_time(self.deck.end),
                                        self.deck.mode,
                                        flags,
                                        meter)

        # Screenshot text.
        if False:
            text = {
                'stopped': '0:00.00 / 3:42.37 stopped [||                  ]',
                'playing': '0:20.85 / 3:42.37 playing [|||                 ]',
                'recording':
                '0:11.37 / 3:42.37 recording * [||||||||            ]',
            }[self.deck.mode]

        self.statusbar.set(text)

    def quit(self):
        self.window.quit()
        self.window.destroy()


def main():
    filename = '~/Desktop/overdub-out.wav'
    expanded_filename = os.path.expanduser(filename)

    if sys.argv[1:]:
        blocks = audio.load(sys.argv[1])
    else:
        blocks = []

    deck = Deck(blocks)
    gui = GUI(deck, filename)

    try:
        gui.mainloop()
    finally:
        deck.close()
        print('\nSaving to {}\n'.format(expanded_filename))
        audio.save(expanded_filename, gui.deck.blocks)


if __name__ == '__main__':
    sys.exit(main())
