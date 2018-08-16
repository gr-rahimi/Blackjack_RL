import blackjack
from blackjack.desk import Desk
from blackjack.player import YusefCardCount, NoCountPlayer

blackjack.number_iters = 100000



d=Desk()
p=NoCountPlayer("Asghar", True)
d.AddPlayer(p)
p=YusefCardCount("Reza", True)
d.AddPlayer(p)



for i in range(blackjack.number_iters):
    d.Play()
    print("_" * 50, i , "_" * 50)


p.setTrain(False)
for i in range(1000):
    d.Play()
    print("_" * 50, i , "_" * 50)
