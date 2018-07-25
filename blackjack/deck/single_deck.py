from . import single_card
from random import shuffle

class SingleDeck(object):

    def __init__(self, need_shuffle = True):
        self._items=[single_card.SingeCard(s,v) for s in single_card.Shape for v in range(1,14)]
        if need_shuffle:
            shuffle(self._items)


    def get_cards(self):
        return self._items


