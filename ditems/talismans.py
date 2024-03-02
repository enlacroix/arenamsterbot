from ditems.itemcls import Item


class Talisman(Item):
    talismanSummonsDict = {741: (summon_classes.misc.EvilTree, 'Кошмарная упырица вступает в битву!'), }

    def __init__(self, code: int):
        super().__init__(code)

    def setCharge(self, amount):
        self.charges += amount  # При каких-то условиях (навыках, перках)

    def use(self, owner, other, ctx):
        if self.code == 461:
            # Нестандартный талисман высшей защиты с зарядами.
            pass
        else:
            creature, msg = Talisman.talismanSummonsDict[self.code]
            if owner.createSummon(creature, ctx):
                send(ctx, msg)
                return 1
            else:
                return -1