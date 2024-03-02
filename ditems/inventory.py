from functools import reduce



class Inventory:
    """
    Каждому существу с помощью композиции (self.inv = Inventory(стартовые предметы: Item)) присвоен такой объект.
    """

    def __init__(self, owner=None, *startItems):
        item_lst = list(startItems)
        self.pool = dict(zip(item_lst, [1] * len(item_lst)))
        self.owner = owner

    def __str__(self):
        """
        private: С возможностью отправки в личные сообщения. if private: ls_send(ctx, output)
        """
        if len(self) == 0: return 'Инвентарь пуст.'
        return reduce(lambda a, item:
        a + f'{item.getPosition(self)}. {item.name}, {item.getAmount(self)} шт. {item.showAbility(self.owner)} \n {item.description}. \n', self.pool, '')


    def clearInventory(self):
        self.pool.clear()

    def __contains__(self, item):
        """ Можно использовать на проверку того, есть ли предмет в инвентаре, тогда он давал бы эффекты. """
        return item in self.pool.keys()

    def __len__(self):
        return len(self.pool)

    # TODO: уничтожить случайную вещь, уничтожить две случайные вещи, уничтожить весь инвентарь, уничтожить конкретную вещь.

    def getItem(self, position: int):
        if 1 <= position <= len(self.content):
            return self.content[position-1] # todo сделать обращение к инвентарю КОМАНДЫ, А НЕ СВОЕМУ
        return

    def showInventoryWithPrices(self) -> str:
        if len(self) == 0: return 'Всё распродано.'
        output = reduce(lambda a, item:
        a + f'{item.getPosition(self)}. {item.show()} ({item.getSalePrice(self.owner)} зол), {item.getAmount(self)} шт. {item.showAbility(self.owner)} \n', self.pool, '')
        return f'{self.owner}: \n {output} Стоимость снаряжения: {self.totalCost} зол.'\
            '\n [прод все] - продать все предметы разом.'

    def addItem(self, item, amount=1):
        if item in self:
            self.pool[item] += amount
        else:
            self.pool[item] = amount
        return 1

    def addSeveralItems(self, things):
        for item in things:
            self.addItem(item)

    def removeItem(self, item, amount=1):
        if item in self:
            self.pool[item] -= amount
            if self.pool[item] <= 0:
                del self.pool[item]
        else:
            return 0

    @property
    def content(self):
        return list(self.pool.keys())

    @property
    def totalCost(self):
        return sum([item.getSalePrice(self.owner) for item in self.pool.keys()])





