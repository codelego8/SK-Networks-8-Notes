import random

from dice.entity.dice import Dice
from dice.repository.dice_repository import DiceRepository


class DiceRepositoryImpl(DiceRepository):
    __instance = None
    __diceList = []

    MIN = 1
    MAX = 6

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return  cls.__instance

    def rollDice(self):
        diceNumber = random.randint(self.MIN, self.MAX)
        dice = Dice(diceNumber)
        self.__diceList.append(dice)

    def rollMultiDice(self, diceCount):
        self.diceCount = diceCount
        for _ in range(self.diceCount):
            self.rollDice()

        return self.__diceList

    def acquireDiceList(self):
        return  self.__diceList





