
class Coin():
    def __init__(self,name,algo,nethash,blockreward,price,blocktime):
        self.name=name
        self.algo=algo
        self.nethash=nethash
        self.blockreward=blockreward
        self.price=price
        self.blocktime=blocktime

    def setX10Rev(self,rev):
        self.x10rev=rev