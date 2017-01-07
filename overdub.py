#!/usr/bin/env python3
"""
http://www.ittc.ku.edu/~niehaus/classes/448-s04/448-standard/simple_gui_examples/index.html
http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
"""
import os
import tkinter
import tkinter.font
from tkinter import *
from overdub import audio
from overdub.deck import Deck

def get_font(size):
    return tkinter.font.Font(family="Helvetica", size=size)


class GUI:
    def __init__(self, filename, blocks):
        self.filename = filename

        self.player = None
        self.recorder = None

        self.undo_blocks = None

        self.root = root = Tk()
        root.title('Overdub')

        label = Label(text='Writing to: ' + self.filename)
        label['font'] = get_font(size=15)
        label.pack(side=TOP,padx=10,pady=10)

        self.statusbar = StringVar()
        label = Label(textvariable=self.statusbar)
        label['font'] = get_font(size=30)
        label.pack(side=TOP,padx=10,pady=10)

        for (text, command) in [
            ('Record', self.record),
            ('Play', self.play),
            ('Stop', self.stop),
            ('Undo', self.undo),
        ]:
            button = Button(root, text=text, command=command)
            button['font'] = get_font(size=30)
            button.pack(side=LEFT)

        self.deck = Deck(blocks)
        self.update_statusbar()

    def update(self):
        self.root.update()
        self.deck.update()

    def mainloop(self):
        try:
            while True:
                self.update()
        except KeyboardInterrupt:
            return

    def play(self):
        self.deck.pos = 0
        self.deck.mode = 'playing'

    def record(self):
        self.undo_blocks = self.deck.blocks.copy()
        self.deck.pos = 0
        self.deck.mode = 'recording'

    def stop(self):
        self.deck.pos = 0
        self.deck.mode = 'stopped'

    def undo(self):
        if self.deck.mode == 'recording':
            self.deck.mode = 'playing'

        if self.undo_blocks is None:
            pass
        else:
            self.deck.blocks[:] = self.undo_blocks
            self.undo_blocks = None

    def update_statusbar(self):
        text = '{} / {} {}'.format(self.deck.pos,
                                   len(self.deck.blocks),
                                   self.deck.mode)
        if self.undo_blocks is not None:
            text += '(undo possible)'
        self.statusbar.set(text)
        self.root.after(50, self.update_statusbar)


filename = os.path.expanduser('~/Desktop/overdub-out.wav')

if sys.argv[1:]:
    blocks = audio.load(sys.argv[1])
else:
    blocks = []

gui = GUI(filename, blocks)

try:
    gui.mainloop()
finally:
    audio.save(filename, gui.deck.blocks)
