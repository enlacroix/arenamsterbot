class ResistState:
    def __init__(self, resist):
        self.obj = resist

    def setImmunity(self):
        self.obj.state = Immunity(self.obj)

    def setDefault(self):
        self.obj.state = DefaultState(self.obj)

    def setWard(self, charges=1):
        self.obj.state = Ward(self.obj, charges)

    def getValue(self):
        return 0


class Ward(ResistState):
    def __init__(self, resist, charges=1):
        super().__init__(resist)
        # Сколько зарядов имеет вард (если два, то нужно две атаки, чтобы его сбить).
        self.charges = charges

    def __str__(self):
        return f'Щит{"" if self.charges <= 1 else f" ({self.charges})"}, {self.obj.value}%'

    def getMultiplier(self):
        """
        :return True: заряды варда закончились, выведи сообщение.
        False: есть заряды.
        """
        self.charges -= 1
        if self.charges == 0:
            self.setDefault()
        return 0

    def setWard(self, charges=1): # Экспериментальная штука
        self.charges += charges

    @staticmethod
    def calcMultiplier():
        return 0


class Immunity(ResistState):
    def __init__(self, resist):
        super().__init__(resist)

    @staticmethod
    def getMultiplier():
        return 0

    @staticmethod
    def calcMultiplier():
        return 0

    def __str__(self):
        return 'Иммунитет'


class DefaultState(ResistState):
    def __init__(self, resist):
        super().__init__(resist)

    def __str__(self):
        return f'{self.obj.value}%'

    def getMultiplier(self):
        if self.obj.value > 0:
            return max(0, 1 - self.obj.value / 100)
        if self.obj.value <= 0:
            return 1 + abs(self.obj.value) / 100

    def calcMultiplier(self):
        return self.getMultiplier()

    def getValue(self):
        return self.obj.value
