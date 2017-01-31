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

        self.statusbar = StringVar()
        label = Label(textvariable=self.statusbar)
        label['font'] = get_font(size=30)
        label.pack(side=TOP,padx=10,pady=10)

        label = Label(text='Writing to: ' + self.filename)
        label['font'] = get_font(size=15)
        label.pack(side=TOP,padx=10,pady=10)

        if False:
            for (text, command) in [
                    ('Record', self.record),
                    ('Play', self.play),
                    ('Stop', self.stop),
                    ('Undo', self.undo),
            ]:
                button = Button(root, text=text, command=command)
                button['font'] = get_font(size=30)
                button.pack(side=LEFT)

        self.root.bind("<KeyPress-Return>", lambda event: self.toggle_record())
        self.root.bind("<KeyPress-space>", lambda event: self.toggle_play())
        self.root.bind("<KeyPress-BackSpace>", lambda event: self.undo())

        self.skipdist = 0
        skipdist = 10

        def add_skipdist(skipdist):
            self.skipdist += skipdist

        # We can't use KeyPress/KeyRelease because of key repeat.
        self.root.bind("<ButtonPress-1>", lambda event: add_skipdist(-skipdist))
        self.root.bind("<ButtonRelease-1>", lambda event: add_skipdist(skipdist))

        self.root.bind("<ButtonPress-2>", lambda event: self.toggle_record())

        self.root.bind("<ButtonPress-3>", lambda event: add_skipdist(skipdist))
        self.root.bind("<ButtonRelease-3>", lambda event: add_skipdist(-skipdist))

        self.deck = Deck(blocks)
        self.update_statusbar()

    def update(self):
        self.root.update()
        self.root.update_idletasks()
        self.deck.update()
        self.skip(self.skipdist)

    def mainloop(self):
        try:
            while True:
                self.update()
        except KeyboardInterrupt:
            return

    def play(self):
        self.deck.mode = 'playing'

    def record(self):
        self.undo_blocks = self.deck.blocks.copy()
        self.deck.mode = 'recording'

    def stop(self):
        self.deck.mode = 'stopped'

    def toggle_play(self):
        if self.deck.mode == 'stopped':
            self.play()
        else:
            self.stop()

    def toggle_record(self):
        if self.deck.mode == 'recording':
            self.play()
        else:
            self.record()

    def skip(self, numblocks=0):
        if numblocks == 0:
            return

        if self.deck.mode == 'recording':
            self.deck.mode = 'playing'

        self.deck.pos += numblocks
        if self.deck.pos < 0:
            self.deck.pos = 0

    def undo(self):
        if self.deck.mode == 'recording':
            self.deck.mode = 'playing'

        if self.undo_blocks is None:
            pass
        else:
            self.deck.blocks[:] = self.undo_blocks
            self.undo_blocks = None

    def update_statusbar(self):
        #text = '{} / {} {}'.format(self.deck.pos,
        #                           len(self.deck.blocks),
        #                           self.deck.mode)
        #if self.undo_blocks is not None:
        #    text += '(undo possible)'

        if (self.deck.pos * audio.SECONDS_PER_BLOCK) <= 1:
            near_start = '.'
        else:
            near_start = ' '

        mode_text = {
            'recording': 'O',
            'playing': '>',
            'stopped': ' ',
        }[self.deck.mode]

        if self.undo_blocks is not None:
            undo_text = '*'
        else:
            undo_text = ' '

        text = '{} {}  {}'.format(near_start, mode_text, undo_text)

        self.statusbar.set(text)
        self.root.after(10, self.update_statusbar)


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
