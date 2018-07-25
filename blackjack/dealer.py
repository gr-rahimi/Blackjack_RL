from .player import Player, Actions

from .deck.single_deck import SingleDeck

from random import shuffle
import numpy as np



class DealerDeck:
    off_percentage, off_deviation, zone_count = 0.2, 3, 4

    def __init__(self, number_of_decks):

        self._nod = number_of_decks
        self._head = 0

        self._total_cards=[]
        for _ in range(number_of_decks):
            self._total_cards.extend(SingleDeck(need_shuffle=True).get_cards())
        self._end = len(self._total_cards)
        self.Shuffle()


    def Shuffle(self):
        for c in self._total_cards:
            c.setVisible(False)
        shuffle(self._total_cards)
        off_dev = np.random.normal(0, DealerDeck.off_deviation)
        self._head = 0
        self._end = len(self._total_cards) - int(DealerDeck.off_percentage * len(self._total_cards) + off_dev)

    def DeckDrawACard(self):
        if self._head == self._end:
            raise  RuntimeError("not enough card in deck")
        self._head +=1
        return self._total_cards[self._head-1]

    def getStr(self):
        p_str = [c.getStr() for c in self._total_cards[self._head:self._end]]
        return "|".join(p_str)

    def NumberRemained(self):
        return self._end - self._head

    def getZone(self):
        zone_size = len(self._total_cards) // self.zone_count
        return self._head // zone_size




class Dealer(Player):

    def __init__(self, number_of_decks):
        super(Dealer, self).__init__("Dealer")
        self._deck = DealerDeck(number_of_decks)
        self.predicted_remaining_cards = 0


    def CanContinue(self, number_of_players):
        remained_card = self.getDeckNumerRemained()
        expected_card = number_of_players * 6
        self.predicted_remaining_cards = remained_card - expected_card
        return expected_card <= remained_card


    def CanSplit(self):
        if self.predicted_remaining_cards > 6:
            self.predicted_remaining_cards -= 6
            return True
        else:
            return False

    def getValue(self):
        assert (not any([not c.IsVisible() for c in self._hand]))
        return super(Dealer, self).getValue()


    def DealerDrawACard(self, v):
        c =self._deck.DeckDrawACard()
        c.setVisible(v)
        return c

    def ShuffleDeck(self):
        self._deck.Shuffle()

    def getAction(self, desk):
        if self.getBestValue(True) >= 17:
            return Actions.Stand
        else:
            return Actions.Hit

    def _getFeature(self, desk):
        pass

    def _getInsuranceFeature(self, desk):
        pass

    def getDeckStr(self):
        return self._deck.getStr()
    def getDeckNumerRemained(self):
        return self._deck.NumberRemained()

    def getZone(self):
        return self._deck.getZone()
















