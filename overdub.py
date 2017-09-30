#!/usr/bin/env python3
"""
http://www.ittc.ku.edu/~niehaus/classes/448-s04/448-standard/simple_gui_examples/index.html
http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
"""
import sys
import tkinter as tk
import tkinter.font
from overdub import audio
from overdub.deck import Deck
from overdub.status_line import make_status_line
from overdub.filenames import make_output_filename
from overdub.gamepad import Gamepad


def get_font(size):
    return tkinter.font.Font(family='Courier', size=size)


class GUI:
    def __init__(self, deck, filename, fullscreen=True):
        self.deck = deck
        self.filename = filename
        self.fullscreen = fullscreen
        self.fast_winding = False

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

        label = tk.Label(text='')
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
            if event['init']:
                continue

            if event['type'] == 'axis':
                if event['code'] == 2:
                    # Right joystick left/right for winding and scrubbing.
                    value = event['value']

                    # Sometimes the gamepad doesn't go all the way back to 0.0.
                    if abs(value) < 0.05:
                        value = 0

                    self.gamepad_skipdist = value
                    self.deck.scrub = bool(value)

                # elif event['code'] == 3:
                #     # Right joystick, pull back for stop push away for play.
                #     value = event['value']
                #
                #     if abs(value) >= 0.7:
                #          if value < 0:
                #            self.deck.play()
                #         else:
                #             self.deck.stop()

            # Right gamepad.
            if (event['type'], event['code']) == ('axis', 2):
                value = event['value']
            elif event['type'] == 'button':
                # Add 1 because buttons are numbered 1-10 on the gamepad.
                button = event['code'] + 1

                if button == 9:
                    self.deck.solo = bool(event['value'])

                elif button == 10:
                    self.fast_winding = bool(event['value'])

                elif event['value'] is True:
                    if button == 1:
                        self.deck.record()
                    elif button == 2:
                        self.deck.stop()
                    elif button == 3:
                        self.deck.play()
                    elif button == 4:
                        self.deck.undo()

                    elif button == 12:
                        # Push right joystick.
                        self.deck.record()

    def update(self):
        self.handle_gamepad()
        self.deck.skip(self.skipdist)

        if self.fast_winding:
            scale = 5
        else:
            scale = 1
        self.deck.skip(self.gamepad_skipdist * scale)

        self.update_display()
        self.window.after(50, self.update)

    def update_display(self):
        # if self.deck.time < 1:
        #     text = '.'
        # else:
        #     text = ''
        # self.statusbar.set(text)
        self.statusbar.set(make_status_line(self.deck))

        background = {'recording': '#a00',  # Red
                      'playing': '#050',  # Green
                      'stopped': 'black'}[self.deck.mode]

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


def main():
    filename = make_output_filename()

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
        if len(deck.blocks) > 0:
            print('\nSaving to {}\n'.format(filename))
            audio.save(filename, gui.deck.blocks)
        else:
            print('\nNothing to save\n')


if __name__ == '__main__':
    sys.exit(main())
