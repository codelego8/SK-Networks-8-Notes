from dice.entity.dice_kinds import DiceKinds
from dice.entity.dice_skill import DiceSkill
from dice.repository.dice_repository_impl import DiceRepositoryImpl
from game.repository.game_repository_impl import GameRepositoryImpl
from game.service.game_service import GameService
from player.repository.player_repository_impl import PlayerRepositoryImpl


class GameServiceImpl(GameService):
    __instance = None

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

    def __createGamePlayer(self):
        gamePlayerCount = self.__gameRepository.getGamePlayerCount()

        for _ in range(gamePlayerCount):
            self.__playerRepository.createName()

    def startDiceGame(self):
        self.__gameRepository.create()

        self.__createGamePlayer()

    def rollFirstDice(self):
        gamePlayerCount = self.__gameRepository.getGamePlayerCount()
        playerIndexList = []
        diceIdList = []

        # 실제 정말 사용자 숫자만큼 반복을 함 (3명이라 가정)
        # 위 가정의 경우 0, 1, 2로 playerIndex가 설정됨
        for playerIndex in range(gamePlayerCount):
            print(f"playerIndex: {playerIndex}")
            # 기존에는 단순히 굴리기만 했음
            # 혹은 굴리고 Dice 객체 자체를 리턴했음
            # 그러나 Player가 어떤 Dice 객체를 소유하고 있는지 판단할 필요가 생겼음
            # 그러므로 rollDice() 이후 생성된 주사위의 고유한 번호(id)를 리턴시켰음
            diceId = self.__diceRepository.rollDice()
            diceIdList.append(diceId)
            # 위의 인덱스는 0부터 시작하지만 Entity 구성의 id가 1부터 시작함
            # 그러므로 발생한 이격을 조정하기 위해 +1을 해서 검색하고 있음
            # findById()를 통해 검색된 Player 객체를 획득
            indexedPlayer = self.__playerRepository.findById(playerIndex + 1)
            print(f"indexedPlayer: {indexedPlayer}")

            playerIndexList.append(playerIndex + 1)

            # Player 엔티티에 setDiceId를 구현하여 획득한 주사위의 번호를 설정함
            # 고로 특정 Player가 특정 Dice의 소유권을 확보하게 되었음
            indexedPlayer.addDiceId(diceId)

        for player in self.__playerRepository.acquirePlayerList():
            print(f"{player}")

        self.__gameRepository.setPlayerIndexListToMap(playerIndexList, diceIdList)

    def __checkSkillAppliedPlayerIndexList(self):
        gamePlayerCount = self.__gameRepository.getGamePlayerCount()
        skillAppliedPlayerList = []

        for playerIndex in range(gamePlayerCount):
            indexedPlayer = self.__playerRepository.findById(playerIndex + 1)
            indexedPlayerDiceIdList = indexedPlayer.getDiceIdList()
            indexedPlayerFirstDiceId = indexedPlayerDiceIdList[0]

            indexedPlayerDice = self.__diceRepository.findById(indexedPlayerFirstDiceId)
            if indexedPlayerDice.getDiceNumber() % 2 == 0:
                skillAppliedPlayerList.append(playerIndex + 1)

        return skillAppliedPlayerList

    def rollSecondDice(self):
        skillAppliedPlayerIndexList = self.__checkSkillAppliedPlayerIndexList()
        skillAppliedPlayerLength = len(skillAppliedPlayerIndexList)
        secondDiceIdList = []

        for index in range(skillAppliedPlayerLength):
            secondDiceId = self.__diceRepository.rollDice()
            secondDiceIdList.append(secondDiceId)

            skillAppliedPlayerIndex = skillAppliedPlayerIndexList[index]
            skillAppliedPlayer = self.__playerRepository.findById(skillAppliedPlayerIndex)
            skillAppliedPlayer.addDiceId(secondDiceId)
            print(f"skillAppliedPlayer: {skillAppliedPlayer}")

            secondDice = self.__diceRepository.findById(secondDiceId)
            secondDice.setDiceKinds(DiceKinds.SPECIAL)
            print(f"secondDice: {secondDice}")

        self.__gameRepository.updatePlayerDiceGameMap(
            skillAppliedPlayerIndexList, secondDiceIdList)

    # 조건: 현재 플레이어(playerId)가 스킬을 사용하는 플레이어(playerIndex + 1)라면:
    def __steelScore(self, playerIndex):
        game = self.__gameRepository.getGame()
        playerDiceGameMap = game.getPlayerDiceGameMap()

        for playerId, diceIdList in playerDiceGameMap.items():
            if playerId == playerIndex + 1:
                firstDiceId = diceIdList[0]  # 첫 번째 주사위 ID
                firstDice = self.__diceRepository.findById(firstDiceId) # 주사위 객체 찾기

                if firstDice:
                    gamePlayerCount = self.__gameRepository.getGamePlayerCount() # 총 플레이어 수
                    diceNumber = firstDice.getDiceNumber() # 3당첨자의 현재 주사위 숫자
                    firstDice.setDiceNumber(diceNumber + 2 * (gamePlayerCount - 1)) # 점수 증가

                continue # 현재 플레이어의 작업이 끝났으므로 다음 반복으로 이동

            # 이 부분은 playerId != playerIndex + 1인 경우 실행됨
            firstDiceId = diceIdList[0] # 플레이어의 첫 번째 주사위 ID
            firstDice = self.__diceRepository.findById(firstDiceId) # 주사위 객체 찾기

            if firstDice:
                diceNumber = firstDice.getDiceNumber() # 현재 주사위 숫자
                firstDice.setDiceNumber(diceNumber - 2) # 점수 감소

    def __deathShot(self):
        game = self.__gameRepository.getGame()
        playerDiceGameMap = game.getPlayerDiceGameMap()

        playerDiceSum = {}

        for playerId, diceIdList in playerDiceGameMap.items():
            diceSum = 0

            for diceId in diceIdList:
                dice = self.__diceRepository.findById(diceId)

                if dice:
                    diceSum += dice.getDiceNumber()

            playerDiceSum[playerId] = diceSum

        for playerId, diceSum in playerDiceSum.items():
            print(f"플레이어 {playerId}의 누산 점수: {diceSum}")

        deathShotTargetPlayerId = int(input('누구를 저격하시겠습니까? '))
        self.__gameRepository.deletePlayer(deathShotTargetPlayerId)

    def __applySkill(self, playerIndex, secondDice):
        secondDiceNumber = secondDice.getDiceNumber()
        print(f"secondDiceNumber: {secondDiceNumber}")

        if secondDiceNumber == DiceSkill.STEEL_SCORE.value:
            self.__steelScore(playerIndex)

        if secondDiceNumber == DiceSkill.DEATH_SHOT.value:
            self.__deathShot()

    def applySkill(self):
        gamePlayerCount = self.__gameRepository.getGamePlayerCount()

        for playerIndex in range(gamePlayerCount):
            indexedPlayer = self.__playerRepository.findById(playerIndex + 1)
            indexedPlayerDiceIdList = indexedPlayer.getDiceIdList()
            indexedPlayerDiceIdListLength = len(indexedPlayerDiceIdList)

            if indexedPlayerDiceIdListLength < 2:
                continue

            indexedPlayerSecondDiceId = indexedPlayerDiceIdList[1]
            secondDice = self.__diceRepository.findById(indexedPlayerSecondDiceId)

            self.__applySkill(playerIndex, secondDice)

    def checkWinner(self):
        # print("checkWinner() called!")

        game = self.__gameRepository.getGame()
        playerDiceGameMap = game.getPlayerDiceGameMap()

        playerDiceSum = {}

        for playerId, diceIdList in playerDiceGameMap.items():
            diceSum = 0

            for diceId in diceIdList:
                dice = self.__diceRepository.findById(diceId)

                if dice:
                    diceSum += dice.getDiceNumber()

            playerDiceSum[playerId] = diceSum

        maxDiceSum = max(playerDiceSum.values())
        maxDicePlayerList = [playerId for playerId, diceSum in playerDiceSum.items()
                             if diceSum == maxDiceSum]

        if len(maxDicePlayerList) > 1:
            print("무승부")
            return

        winnerId = maxDicePlayerList[0]

        winner = self.__playerRepository.findById(winnerId)
        print(f"승자: {winner}")
