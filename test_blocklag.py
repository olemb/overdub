#!/usr/bin/env python3
import time
from overdub.deck import Deck

def test_blocklag():
    deck = Deck()

    while True:
        print('Rewind!')
        deck.pos = 0
        deck.mode = 'recording'
        for i in range(43):
            deck.update()


test_blocklag()
