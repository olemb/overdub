#!/usr/bin/env python3
"""
http://www.ittc.ku.edu/~niehaus/classes/448-s04/448-standard/simple_gui_examples/index.html
http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
"""
import os
import sys
import time
import tkinter
import tkinter.font
from tkinter import *
from overdub import audio
from overdub.deck import Deck
from overdub.gamepad import Gamepad


def get_font(size):
    return tkinter.font.Font(family="Courier", size=size)


class GUI:
    def __init__(self, deck, filename):
        self.deck = deck
        self.filename = filename

        self.gamepad = Gamepad(optional=True)

        self.player = None
        self.recorder = None

        self.root = root = Tk()
        root.title('Overdub')

        root.protocol("WM_DELETE_WINDOW", self.quit)

        self.statusbar = StringVar()
        label = Label(textvariable=self.statusbar)
        label['font'] = get_font(size=30)
        label.pack(side=TOP,padx=10,pady=10)

        label = Label(text=self.filename)
        label['font'] = get_font(size=15)
        label.pack(side=TOP,padx=10,pady=10)

        self.root.attributes("-fullscreen", True)

        if False:
            for (text, command) in [
                    ('Record', self.deck.record),
                    ('Play', self.deck.play),
                    ('Stop', self.deck.stop),
                    ('Undo', self.deck.undo),
            ]:
                button = Button(root, text=text, command=command)
                button['font'] = get_font(size=30)
                button.pack(side=LEFT)

        self.root.bind('<KeyPress-Return>', lambda _: self.deck.toggle_record())
        self.root.bind('<KeyPress-space>', lambda _: self.deck.toggle_play())
        self.root.bind('<KeyPress-BackSpace>', lambda _: self.deck.undo())

        self.root.bind('<ButtonPress-2>', lambda _: self.deck.toggle_record())

        self.skipdist = 0

        def skip_less(_):
            self.skipdist -= 1
            
        def skip_more(_):
            self.skipdist += 1

        self.gamepad_skipdist = 0

        # We can't use KeyPress/KeyRelease because of key repeat.
        self.root.bind('<ButtonPress-1>', skip_less)
        self.root.bind('<ButtonRelease-1>', skip_more)

        self.root.bind('<ButtonPress-3>', skip_more)
        self.root.bind('<ButtonRelease-3>', skip_less)

        self.root.bind('<KeyPress-Left>', skip_less)
        self.root.bind('<KeyRelease-Left>', skip_more)

        self.root.bind('<KeyPress-Right>', skip_more)
        self.root.bind('<KeyRelease-Right>', skip_less)

        self.update()

    def handle_gamepad(self):
        for event in self.gamepad.events:
            # Right gamepad.
            if (event['type'], event['code']) == ('axis', 2):
                value = event['value']

                # Sometimes the gamepad doesn't go all the way back to 0.0.
                if abs(value) < 0.01:
                    value = 0

                if value >= 0:
                    sign = 1
                else:
                    sign = -1

                value = (abs(value) ** 4) * 4 * sign
                
                self.gamepad_skipdist = value

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
        # self.root.update()
        self.handle_gamepad()
        self.deck.skip(self.skipdist)
        self.deck.skip(self.gamepad_skipdist)
        self.update_display()

        bg = {'recording': 'red',
              'playing': 'green',
              'stopped': 'black'}[self.deck.mode]
        self.root.configure(background=bg)

        self.root.after(50, self.update)

    def mainloop(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            return
        finally:
            pass

    def update_display(self):
        if self.deck.undo_blocks is not None:
            undo_text = ' (undo)'
        else:
            undo_text = ''

        if self.deck.solo:
            solo_text = ' (solo)'
        else:
            solo_text = ''

        text = '{:02.2f} / {:02.2f} {}{}{}'.format(self.deck.time,
                                                   self.deck.end,
                                                   self.deck.mode,
                                                   undo_text,
                                                   solo_text)

        meter = '#' * int(self.deck.meter * 20)
        text += ' [{}]'.format(meter.ljust(20))

        self.statusbar.set(text)

    def quit(self):
        self.root.quit()
        self.root.destroy()


def main():
    filename = os.path.expanduser('~/Desktop/overdub-out.wav')

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
        print('\nSaving to {}\n'.format(filename))
        audio.save(filename, gui.deck.blocks)


if __name__ == '__main__':
    sys.exit(main())
