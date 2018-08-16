from .dealer import Dealer
from .player import Actions, InsuranceActions
import numpy as np
from itertools import chain
from .stat import Stat
import matplotlib.pyplot as plt
import blackjack

plt.ion()

class CardCount(object):
    def __init__(self):
        self._value=[0,0]

    def AddCard(self, c):
        if not c.IsVisible(): # we do not count invisible cards
            return
        if c.IsAce():
            self._value[0]+=1
        else:
            if c.getValue()<= 6:
                self._value[1]+=1
            elif c.getValue()>=10:
                self._value[0]+=1

    def Reset(self):
        self._value =[0,0]

    def getCount(self):
        return tuple(self._value)


class Desk(object):
    DeskCapacity = 4

    def __init__(self):
        self._players = [[]]* Desk.DeskCapacity
        self._dealer = Dealer(blackjack.deck_count)
        self._card_counter = CardCount()
        self._number_of_players = 0
        self._fig, self._ax = plt.subplots()
        #self._stat = Stat(self._fig , self._ax, 100, int(blackjack.number_iters/ 100))



    def AddPlayer(self, player, seat_index = -1):
        player.setStat(Stat(self._fig , self._ax, 100, int(blackjack.number_iters/ 100)))
        self._ax.legend()
        if seat_index == -1:
            for p_idx, same_players in enumerate(self._players):
                if len(same_players) == 0:
                    self._players[p_idx] = [player]
                    self._number_of_players+=1
                    return
            raise RuntimeError("Not enough space")
        else:
            self._players[seat_index] = [player]
            self._number_of_players+=1

    def Play(self):
        if not self._dealer.CanContinue(self.getNumberofPlayers(True) + 1):
            self._card_counter.Reset()
            self._dealer.ShuffleDeck()
            assert self._dealer.CanContinue(self.getNumberofPlayers(True)) # this is necessary. Need to be fixed(split)

        print ("Deck({})={}".format( self._dealer.getDeckNumerRemained(),
                                     self._dealer.getDeckStr(self.getNumberofPlayers(True) * Dealer.average_card_per_player)))

        print(self.getPlayersNames())



        for same_players in chain(self._players, [[self._dealer]]):
            if len(same_players) == 0:
                continue
            assert len(same_players) ==1 , "initialy we do not have split players"
            same_players[0].InitializeNewHand()

        self._dealer.InitializeNewHand()
        self._distribute_initial_cards()


        strHandList=[]
        strFormat="{:97}" * (self.getNumberofPlayers(True) + 1)
        for players_list in chain(self._players, [[self._dealer]]):
            if len(players_list)== 0:
                continue
            initialHand = players_list[0].getHand()
            strHandList.append(initialHand[0].getStr() + "|" + initialHand[1].getStr())
        print(strFormat.format(*strHandList))

        delaer_black_jack = self._dealer.HasBlackJack()
        if self._dealer.HowManyAce(True) == 1:
            for same_players in self._players:
                if len(same_players) == 0:
                    continue
                _ =same_players[0].getInsuranceAction(self)
                same_players[0].PostInsurance(self)

        if delaer_black_jack:
            return # dealer has black jack


        valid_player_idx = 0
        for players_list in self._players:
            if len(players_list) == 0:
                continue
            for p in players_list:
                if p._split_player:
                    card = self._dealer.DealerDrawACard(v=True)
                    self._card_counter.AddCard(card)
                    p.AddCardToHand(card)
                    p.PostAction()
                    initialHand = p.getHand()
                    print("Splitted Hand:",initialHand[0].getStr() + initialHand[1].getStr())
                else:
                    valid_player_idx += 1
                while True: # single hand
                    toPrintStr = ""
                    toPrintStr += p.getStateStr(self)
                    action = p.getAction(self)
                    if action == Actions.Hit.value:
                        toPrintStr += "|Hit"
                        card = self._dealer.DealerDrawACard(v = True)
                        toPrintStr += ("|" +card.getStr())
                        self._card_counter.AddCard(card)
                        p.AddCardToHand(card)
                        if p.IsBusted():
                            print(("{:60}"*valid_player_idx).format(*["" if i < valid_player_idx-1
                                                                      else toPrintStr for i in range(valid_player_idx)]))
                            toPrintStr =""
                            break
                        else:
                            p.PostAction(self)
                            toPrintStr += ("|R=" + p.getRewardStr(self))
                            print(("{:60}" * valid_player_idx).format(*["" if i < valid_player_idx - 1
                                                                        else toPrintStr for i in
                                                                        range(valid_player_idx)]))
                            #print(toPrintStr)
                            continue
                    elif action == Actions.Split.value:
                        toPrintStr += "|Split"
                        new_player = p.PostSplit(self)
                        same_players.append(new_player) # needs to be fixed
                        card = self._dealer.DealerDrawACard(v=True)
                        toPrintStr += ("|" + card.getStr())
                        self._card_counter.AddCard(card)
                        p.AddCardToHand(card)
                        p.PostAction()
                        toPrintStr += ("|R=" + p.getRewardStr(self))
                        print(("{:60}" * valid_player_idx).format(*["" if i < valid_player_idx - 1
                                                                    else toPrintStr for i in range(valid_player_idx)]))
                        #print(toPrintStr)
                        continue
                    elif action == Actions.Stand.value:
                        toPrintStr += "|Stand"
                        #print(toPrintStr)
                        print(("{:60}" * valid_player_idx).format(*["" if i < valid_player_idx - 1
                                                                    else toPrintStr for i in range(valid_player_idx)]))
                        toPrintStr =""
                        break
                    elif action == Actions.Surrender.value:
                        toPrintStr += "|Surrender"
                        print(("{:60}" * valid_player_idx).format(*["" if i < valid_player_idx - 1
                                                                    else toPrintStr for i in range(valid_player_idx)]))
                        #print(toPrintStr)
                        toPrintStr =""
                        break
                    elif action == Actions.Double.value:
                        toPrintStr += "|Double"
                        card = self._dealer.DealerDrawACard(v=True)
                        toPrintStr += ("|" + card.getStr())
                        print(("{:60}" * valid_player_idx).format(*["" if i < valid_player_idx - 1
                                                                    else toPrintStr for i in range(valid_player_idx)]))
                        #print(toPrintStr)
                        toPrintStr = ""
                        self._card_counter.AddCard(card)
                        p.AddCardToHand(card)
                        break

        self._dealer.getHand()[1].setVisible(True)
        self._card_counter.AddCard(self._dealer.getHand()[1])

        dealer_should_play = False
        for same_players in self._players:
            if len(same_players) == 0:
                continue
            else:
                for p in same_players:
                    if p.IsBusted() or p.getLastAction()== Actions.Surrender.value:
                        continue
                    else:
                        dealer_should_play = True
                        break


        while dealer_should_play:
            dealer_action = self._dealer.getAction(self)
            if dealer_action == Actions.Stand:
                print((("{:60}" * valid_player_idx)+"{:75}").format(*["" if i < valid_player_idx
                                                                    else "Stand" for i in range(valid_player_idx+1)]))
                #print("{:60}{:75}".format("","Stand"))
                break
            elif dealer_action == Actions.Hit:
                card = self._dealer.DealerDrawACard(v=True)
                self._card_counter.AddCard(card)
                self._dealer.AddCardToHand(card)
                dealer_str = "Hit" + card.getStr()
                print((("{:60}" * valid_player_idx) + "{:50}").format(*["" if i < valid_player_idx
                                                                        else dealer_str for i in
                                                                        range(valid_player_idx + 1)]))
                #print("{:60}{:50}".format("",dealer_str))
                if self._dealer.IsBusted():
                    break

        valid_player_idx = 0
        for same_players in self._players:
            if len(same_players) == 0:
                continue
            valid_player_idx +=1

            for p in same_players:
                p.PostAction(self)
                reward_str = p.getRewardStr(self)
                toPrintStr = ("R=" + reward_str)
                p._stat.AddSample(float(reward_str))
                print(("{:60}"*valid_player_idx).format(*["" if i < valid_player_idx -1 else toPrintStr for i in range(valid_player_idx)]))

                if p._split_player:
                    del p


    def _distribute_initial_cards(self):
        for i in range(2):
            card = self._dealer.DealerDrawACard(v = (i == 0)) # invisible card of dealer
            self._card_counter.AddCard(card)
            self._dealer.AddCardToHand(card)
            for same_players in self._players:
                if len(same_players) == 0:
                    continue
                card = self._dealer.DealerDrawACard(v = True)
                self._card_counter.AddCard(card)
                same_players[0].AddCardToHand(card)


    def getDealer(self):
        return self._dealer

    def getCardCount(self):
        return self._card_counter.getCount()

    def getReducedCardCount(self):
        cc = self._card_counter.getCount()
        if cc[0]>cc[1]:
            return (cc[0]-cc[1],0)
        else:
            return (0,cc[1]-cc[0])


    def getValidActions(self, player):

        out_set = np.zeros(len(Actions), dtype=float)

        if player.IsBusted():
            return out_set

        if player.getNumberofCards() == 2:
            if player.HasBlackJack():
                out_set[Actions.Stand.value] = 1.0
            else:
                out_set[Actions.Surrender.value]= 1.0
                out_set[Actions.Double.value] = 1.0
                out_set[Actions.Hit.value] = 1.0
                out_set[Actions.Stand.value] = 1.0
                if player.getHand()[0] == player.getHand()[1] and self._dealer.CanSplit():
                    out_set[Actions.Split.value] = 1.0
        else:
            if player.getBestValue(True) < 21:
                out_set[Actions.Hit.value] = 1.0
            out_set[Actions.Stand.value] = 1.0

        return out_set

    def getNumberofPlayers(self, only_real):
        assert only_real == True
        return self._number_of_players



    def getPlayersNames(self):
        players = [same_players[0].getName() for same_players in self._players if len(same_players) >0]
        players.append(self._dealer.getName())
        reversed(players)
        out = "".join(["{:60}" for _ in range(self.getNumberofPlayers(True) + 1)])
        out = out.format(*players)
        return out





























