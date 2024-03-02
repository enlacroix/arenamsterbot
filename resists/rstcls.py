from resists.rststates import DefaultState, Ward, Immunity

class Resist:
    def __init__(self, value, state=DefaultState):
        self.value = value
        self.state = state(self)


    def __str__(self):
        """
        Мы делегируем полю Состояние выведение на экран данных.
        :return: в зависимости от состояния будет возвращать надписи (вард, иммун, значение %)
        """
        return self.state.__str__()

    def setWard(self, charges=1):
        self.state.setWard(charges)

    def setImmunity(self):
        self.state.setImmunity()

    def setDefault(self):
        self.state.setDefault()

    def getValue(self):
        self.state.getValue()

    def changeValue(self, amount):
        self.value += amount

    def hasWardOrImmunity(self):
        return isinstance(self.state, (Ward, Immunity))

    def getMultiplier(self):
        return self.state.getMultiplier()

    def calcMultiplier(self):
        return self.state.calcMultiplier()

