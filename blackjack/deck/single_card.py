from enum import Enum

class bcolors:
    RED = "\033[1;31m"
    RESET = "\033[0;0m"
    BGreyRED = "\033[0;31;47m"
    BgreyBlack = "\033[0;30;47m"

class Shape(Enum):
    Clover = 1
    Pikes = 2
    Hearts = 3
    Diamonds =4

class SingeCard(object):
    Clover = "\u2663"
    Hearts = "\u2665"
    Diamonds = "\u2666"
    Pikes = "\u2660"

    def __init__(self, shape, value):
        self._value = value
        self._shape = shape
        self._visible = False




    def IsAce(self):
        return self._value == 1


    def getValue(self):
        if self._value == 1:
            return (11, 1)
        elif self._value > 10:
            return 10
        else:
            return self._value

    def IsVisible(self):
        return self._visible

    def setVisible(self, v):
        self._visible = v

    def getStr(self):
        result= u""

        if self._shape == Shape.Diamonds:
            if self._visible:
                result += bcolors.RED+SingeCard.Diamonds+bcolors.RESET
            else:
                result += bcolors.BGreyRED + SingeCard.Diamonds + bcolors.RESET
        elif self._shape == Shape.Clover:
            if self._visible:
                result += bcolors.RESET + SingeCard.Clover + bcolors.RESET
            else:
                result += bcolors.BgreyBlack + SingeCard.Clover + bcolors.RESET
        elif self._shape == Shape.Hearts:
            if self._visible:
                result += bcolors.RED+SingeCard.Hearts +bcolors.RESET
            else:
                result += bcolors.BGreyRED + SingeCard.Hearts + bcolors.RESET
        else:
            if self._visible:
                result += bcolors.RESET + SingeCard.Pikes + bcolors.RESET
            else:
                result += bcolors.BgreyBlack + SingeCard.Pikes + bcolors.RESET

        if self._value == 1:
            return result + (bcolors.BgreyBlack if not self._visible else "")+ "A" +bcolors.RESET
        elif self._value == 13:
            return result + (bcolors.BgreyBlack if not self._visible else "")+ "K" +bcolors.RESET
        elif self._value == 12:
            return result + (bcolors.BgreyBlack if not self._visible else "")+ "Q" +bcolors.RESET
        elif self._value == 11:
            return result + (bcolors.BgreyBlack if not self._visible else "")+ "J" +bcolors.RESET
        else:
            return result + (bcolors.BgreyBlack if not self._visible else "")+ str(self._value) + bcolors.RESET








