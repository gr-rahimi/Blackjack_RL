from enum import Enum
from collections import defaultdict
import numpy as np
from abc import abstractmethod, ABC
import random
import blackjack


class Actions(Enum):
    Hit = 0
    Stand = 1
    Double = 2
    Split = 3
    Surrender = 4

class InsuranceActions(Enum):
    NotTaken = 0
    Taken = 0

class Player(ABC):
    def __init__(self, name, dic = None, card = None):
        if dic == None:
            self._hand=[]
            self._policy = {}
            self._insurance_policy = {}
            self._name = name
            #self._split_hands_qu = deque()
            self._split_player = False
        else:
            self._split_player = True
            self._policy = dic
            self._name = name
            self._split_player = True
            self._hand = [card]



    def HasBlackJack(self):
        if len(self._hand) == 2 and self.getBestValue(False) == 21:
            return True
        else:
            return False

    def getHand(self):
        return tuple(self._hand)

    def getValueWA(self, only_visible):
       return sum([c.getValue() if (c.IsVisible() or not only_visible) and not c.IsAce() else 0 for c in self._hand])

    def getBestValue(self, only_visible):
        na = self.HowManyAce(only_visible)
        sum = self.getValueWA(only_visible) + na
        for _ in range(na):
            if sum + 10 > 21:
                break
            else:
                sum += 10
        return sum

    def IsBusted(self):
        return self.getBestValue(True) > 21


    def HowManyAce(self, only_visible):
        return sum([1 if (c.IsVisible() or not only_visible) and c.IsAce() else 0 for c in self._hand])

    def InitializeNewHand(self):
        self._hand = []

    def AddCardToHand(self, card):
        self._hand.append(card)

    def getAction(self, desk):
        return self._policy[self._getFeature(desk)]

    def getInsuranceAction(self, desk):
        return self._insurance_policy[self._getInsuranceFeature(desk)]

    def getNumberofCards(self):
        return len(self._hand)

    @abstractmethod
    def _getFeature(self, desk):
        pass

    @abstractmethod
    def _getInsuranceFeature(self, desk):
        pass


    def SplitHand(self, data = None ):
        card = self._hand[1]
        del self._hand[1]
        return card

    def getName(self):
        return self._name

    def getStateStr(self, desk):
        return str(self._getFeature(desk))





class WikiPlayer(Player):
    def __init__(self):
        super(WikiPlayer, self).__init__()

        #TODO fill in the policy dictionary


    def _getFeature(self, desk):
        pass

    def _getInsuranceFeature(self, desk):
        pass


class EpsilonGreedy(ABC):
    def __init__(self, actions):
        self.actions = actions

    def getProbabilities(self, desk, player):
        valid_actions = desk.getValidActions(player)
        return valid_actions/np.sum(valid_actions)

    @abstractmethod
    def getAction(self, desk, player, besta_ction):
        pass

class FixedEpsilonGreedy(EpsilonGreedy):
    def __init__(self, prob_of_random, actions):
        super(FixedEpsilonGreedy, self).__init__(actions)
        self._prob_of_random = prob_of_random

    def getAction(self, desk, player, best_action):
        select_random = random.uniform(0, 1)
        if select_random < self._prob_of_random:
            random_action= self.getProbabilities(desk, player)
            return np.random.choice(np.arange(len(self.actions)), p = random_action)
        else:
            return np.random.choice(best_action, p = np.ones(len(best_action), dtype= float)/len(best_action))


class IncrementalEpsilonGreedy(EpsilonGreedy):
    def __init__(self, start_random, end_random, iterations, actions):
        super(IncrementalEpsilonGreedy, self).__init__(actions)
        self._de = (float(start_random) - end_random) / iterations
        self._p = start_random
        self._end = end_random

    def getAction(self, desk, player, best_action):
        if(self._p > self._end):
            self._p -=self._de
        select_random = random.uniform(0, 1)
        if select_random < self._p:
            random_action= self.getProbabilities(desk, player)
            return np.random.choice(np.arange(len(self.actions)), p = random_action)
        else:
            return np.random.choice(best_action, p = np.ones(len(best_action), dtype= float)/len(best_action))


class Agent(Player):

    def __init__(self,is_train, q_dict, e_greedy, card, name, state):
        super(Agent, self).__init__(name, None, card)
        self._is_train = is_train
        if q_dict == None:
            self._q = defaultdict(lambda: np.zeros(len(Actions)))
            self._insurance_q = defaultdict(lambda :np.zeros(len(InsuranceActions)))
            self._trainig = True
            self._previous_state_action = (None, None)
            self._insurance_previous_state_action = (None,None)
            #self._e_greedy = FixedEpsilonGreedy(prob_of_random= 0.1, actions=Actions)
            self._e_greedy = IncrementalEpsilonGreedy( start_random = 1.0, end_random= 0.0,
                                                       iterations= int(0.9 * blackjack.number_iters), actions = Actions)

            Agent._discount_factor = 0.95
            Agent._learning_rate = 0.99
        else:
            self._q = q_dict
            self._previous_state_action = (state, Actions.Split)
            self._e_greedy = e_greedy

    def getAction(self, desk):
        s = self._getFeature(desk)
        q = self._q[s]
        q =q.copy()
        valid_actions = desk.getValidActions(self)
        best_q = q[np.argwhere(valid_actions == 1.0)]
        indexes = np.argwhere(q == np.amax(best_q)).flatten()
        filtered_indexes = []
        for i in indexes:
            if valid_actions[i] == 1.0:
                filtered_indexes.append(i)
        if self._is_train:
            new_action = self._e_greedy.getAction(desk, self, filtered_indexes)
        else:
            new_action =  random.choice(filtered_indexes)

        self._previous_state_action = (s, new_action)
        return new_action

    def getInsuranceAction(self, desk):
        s = self._getInsuranceFeature(desk)
        new_action = np.random.choice([InsuranceActions.NotTaken, InsuranceActions.Taken], p=[0.5,0.5])
        self._insurance_previous_state_action = (s, new_action)
        return new_action




    def _getInsuranceFeature(self, desk):
        return (self.getBestValue(True),desk.getReducedCardCount())

    def _get_reward(self, desk):
        reward = 0.0
        if self._previous_state_action[1] == Actions.Stand.value:
            if desk.getDealer().IsBusted():
                reward = 1.0
            elif self.getBestValue(True) > desk.getDealer().getBestValue(True):
                reward = 1.0
            elif self.getBestValue(True) == desk.getDealer().getBestValue(True):
                reward = 0.0
            else:
                reward = -1.0
        elif self._previous_state_action[1] == Actions.Hit.value:
            if self.IsBusted():
                if desk.getDealer().IsBusted():
                    reward = 0.0
                else:
                    reward = -1.0
            else:
                reward = 0.0
        elif self._previous_state_action[1] == Actions.Double.value:
            if self.IsBusted() and desk.getDealer().IsBusted():
                reward = 0.0
            elif desk.getDealer().IsBusted():
                reward = 2.0
            elif self.IsBusted() or self.getBestValue(True) < desk.getDealer().getBestValue(True):
                reward = -2.0
            elif self.getBestValue(True) > desk.getDealer().getBestValue(True):
                reward = 2.0
            else:
                reward = 0.0
        elif self._previous_state_action[1]== Actions.Split.value:
            reward = 0.0  # we need to sum both new hands hear
        elif self._previous_state_action[1]== Actions.Surrender.value:
            reward = -0.5

        return reward

    def getRewardStr(self, desk):
        return str(self._get_reward(desk))

    def _get_insurance_reward(self, desk):
        if desk.getDealer().HasBlackJack():
            return 1.0
        else:
            return -0.5

    def InitializeNewHand(self):
        self._previous_state_action = (None, None)
        super(Agent, self).InitializeNewHand()

    def getLastAction(self):
        return self._previous_state_action[1]

    def setTrain(self, is_train):
        self._is_train = is_train

    def setStat(self, stat):
        self._stat = stat
        self._stat.setName(self._name)



class QlearningOff(Agent):
    def __init__(self, name, is_train, original_state = None, e_greedy = None,  q = None, card = None ):
        super(QlearningOff, self).__init__( is_train, q, e_greedy, card, name, original_state)


    def PostAction(self, desk):
        if self._is_train == False:
            return
        reward = self._get_reward(desk)
        new_s = self._getFeature(desk)
        new_q = self._q[new_s]
        prev_values = self._q[self._previous_state_action[0]]

        valid_actions = desk.getValidActions(self)
        best_q = new_q[np.argwhere(valid_actions == 1.0)]

        best_next_value = np.amax(best_q) if len(best_q) > 0  else 0.0
        prev_values[self._previous_state_action[1]] = prev_values[self._previous_state_action[1]] * self._learning_rate +\
                                                          (1-self._learning_rate)*(reward + self._discount_factor * best_next_value)

    def PostSplit(self, desk):
        split_card = self.SplitHand()
        return QlearningOff(self.getName() +"splited",self._is_train,self._getFeature(desk),self._e_greedy ,self._q, split_card)

    def PostInsurance(self, desk):
        reward = self._get_insurance_reward(desk)
        prev_values = self._insurance_q[self._insurance_previous_state_action[0]]
        prev_values[self._insurance_previous_state_action[1].value] = self._learning_rate * prev_values[self._insurance_previous_state_action[1].value] +\
                                                                 (1 - self._learning_rate) * reward

class YusefCardCount(QlearningOff):
    def __init__(self, name, is_train, original_state = None, e_greedy = None,  q = None, card = None):
        super(YusefCardCount, self).__init__(name, is_train, original_state = None, e_greedy = None,  q = None, card = None)


    def _getFeature(self, desk):
        number_ace_me = self.HowManyAce(True)
        dealer_value = desk.getDealer().getBestValue(True)
        min_playr_value = self.getValueWA(True)
        card_count = desk.getReducedCardCount()
        return(number_ace_me, dealer_value, min_playr_value, card_count, desk.getDealer().getZone())



class NoCountPlayer(QlearningOff):
    def __init__(self, name, is_train, original_state = None, e_greedy = None,  q = None, card = None):
        super(NoCountPlayer, self).__init__(name, is_train, original_state = None, e_greedy = None,  q = None, card = None)


    def _getFeature(self, desk):
        number_ace_me = self.HowManyAce(True)
        dealer_value = desk.getDealer().getBestValue(True)
        min_playr_value = self.getValueWA(True)
        return(number_ace_me, dealer_value, min_playr_value)


