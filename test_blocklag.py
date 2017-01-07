#!/usr/bin/env python3
import time
from overdub.deck import Deck

def test_blocklag():
    def do_blocks(deck, n):
        for _ in range(n):
            deck.handle_block()


    deck = Deck()


    while True:
        print('Rewind!')
        deck.pos = 0
        deck.mode = 'recording'
        do_blocks(deck, 43)


test_blocklag()
