from blackjack.desk import Desk
from blackjack.player import QlearningOff


d=Desk()
p=QlearningOff("Reza", True)
d.AddPlayer(p)



for i in range(200000):
    d.Play()
    print("_" * 50, i , "_" * 50)


p.setTrain(False)
for i in range(1000):
    d.Play()
    print("_" * 50, i , "_" * 50)
