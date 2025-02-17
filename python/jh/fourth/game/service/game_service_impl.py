from game.service.game_service import GameService
from dice.repository.dice_repository_impl import DiceRepositoryImpl
from player.repository.player_repository_impl import PlayerRepositoryImpl
from game.repository.game_repository_impl import GameRepositoryImpl

class GameServiceImpl(GameService):

    __instance = None
    # __playerScoreDic = {} # key-value 값으로 묶어서  큰 값을 리턴해 check winner 할 수 없나

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

            # Service Layer에서 Repository Layer를 연결하는 방법
            cls.__instance.__gameRepository = GameRepositoryImpl.getInstance()
            cls.__instance.__playerRepository = PlayerRepositoryImpl.getInstance()
            cls.__instance.__diceRepository = DiceRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

# 얘는 애초에 플레이어 "둘"이서 게임하는걸 기반으로 설계된 함수이다
    def startDiceGame(self):
        print("StartDiceGame() called!")
        playerNameList = self.__playerRepository.getPlayerNameList()
        self.__diceRepository.rollDice() # 한번 굴렸고
        eachPlayerDiceList = self.__diceRepository.rollDice() #두번 굴렸다

        self.__gameRepository.start(
            playerNameList, eachPlayerDiceList)

    def checkWinner(self):
        print("checkWinner() called!")
        self.__gameRepository.checkWinner()

