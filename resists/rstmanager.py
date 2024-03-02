from datastore.dsources import SRC
from resists.rstcls import Resist
from resists.rststates import Ward, Immunity


class ResistManager:
    def __init__(self, pool: dict[SRC, Resist] = None):
        """
        Словарь вида key: Sources.SOURCE : Resist(value, state).
        ResistManager({Sources.FIRE: Resist(50), Sources.AIR: Resist(10, Ward), Sources.POLYMORPH: Resist(-10, Immunity)})
        """
        self.pool = {} if pool is None else pool

    def __getitem__(self, item: SRC) -> Resist:
        if not item in self.pool: self.pool[item] = Resist(0)
        return self.pool[item]

    def changeValue(self, key: SRC, value):
        if key in self.pool:
            self.pool[key].changeValue(value)
        else:
            self.pool[key] = Resist(value)

    def changeSeveralResists(self, sources: tuple[SRC, ...], value: int):
        for src in sources:
            self.changeValue(src, value)

    @classmethod
    def anonConstructor(cls, *args):
        """ конструктор для понимания которого не нужен импорт Resist и типов State
        пример: (0,), (10, Ward), """
        pass

    def __str__(self):
        return ', '.join([pair[0].value + ': ' + str(pair[1]) for pair in self.pool.items() if pair[1].value != 0 or pair[1].state.__class__ in (Ward, Immunity)])



