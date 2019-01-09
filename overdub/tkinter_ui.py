"""
http://www.ittc.ku.edu/~niehaus/classes/448-s04/448-standard/simple_gui_examples/index.html
http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
"""
import os
import tkinter as tk
import tkinter.font
from . import audio
from .status_line import format_status
from .commands import TogglePlay, ToggleRecord, Skip
from .deck import Deck


def get_font(size):
    return tkinter.font.Font(family='Courier', size=size)


class GUI:
    def __init__(self, deck, filename, minimalist=False, fullscreen=True):
        self.deck = deck
        self.filename = filename
        self.minimalist = minimalist
        self.fullscreen = fullscreen

        self.window = tk.Tk()
        self.window.title('Overdub')

        self.window.protocol("WM_DELETE_WINDOW", self.quit)

        self.statusbar = tk.StringVar()
        label = tk.Label(textvariable=self.statusbar)
        label['font'] = get_font(size=30)
        label['foreground'] = 'white'
        label.pack(side=tk.TOP, padx=10, pady=10)
        self.statusbar_label = label

        label = tk.Label(text='')
        label['font'] = get_font(size=15)
        label['foreground'] = 'white'
        label.pack(side=tk.TOP, padx=10, pady=10)
        self.filename_label = label

        do = self.deck.do

        self.window.bind('<KeyPress-Return>', lambda *_: do(ToggleRecord()))
        self.window.bind('<KeyPress-space>', lambda *_: do(TogglePlay()))
        self.window.bind('<KeyPress-Left>', lambda *_: do(Skip(-1)))
        self.window.bind('<KeyPress-Right>', lambda *_: do(Skip(1)))

        self.window.bind('<KeyPress-f>', lambda *_: self.toggle_fullscreen)

        self.window.attributes("-fullscreen", self.fullscreen)

        self.update()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.window.attributes("-fullscreen", self.fullscreen)

    def update(self):
        self.update_display(self.deck.get_status())
        self.window.after(50, self.update)

    def update_display(self, status):
        if self.minimalist:
            flags = []

            if status.time < 1:
                flags.append('.')

            self.statusbar.set(' '.join(flags))
        else:
            self.statusbar.set(format_status(status))

        background = {'recording': '#a00',  # Red
                      'playing': '#050',  # Green
                      'stopped': 'black'}[status.mode]

        for widget in [self.window, self.statusbar_label, self.filename_label]:
            widget['background'] = background

    def mainloop(self):
        try:
            self.window.mainloop()
        except KeyboardInterrupt:
            return
        finally:
            pass

    def quit(self):
        self.window.quit()
        self.window.destroy()


def ui(filename, minimalist=False):
    deck = Deck()

    if os.path.exists(filename):
        deck.load(filename)

    gui = GUI(deck, filename, minimalist=minimalist)

    try:
        gui.mainloop()
    finally:
        deck.close()
        if len(deck.blocks) > 0:
            print(f'\nSaving to {filename}\n')
            deck.save(filename)
        else:
            print('\nNothing to save\n')
