from collections import namedtuple
from string import Template

Params = namedtuple("Params", "nm hp dmg arm ini ddg luck mrl mana pwr gold acc")

# TODO ЗАМЕНИТЬ НАЗВАНИЯ КЛАССОВ НА ENUM ДЛЯ УДОБСТВА НАБОРА.


stats_dict = {
      'Assassin': Params('Ассасин', 200, dmg=28, arm=0, ini=48, ddg=10, luck=20, mrl=-10, mana=8, pwr=15, gold=350, acc=92), # todo вернуть 48 ини
      'Paladin': Params('Святой мститель', 230, dmg=16, arm=15, ini=46, ddg=0, luck=5, mrl=0, mana=8, pwr=28, gold=350, acc=95),
      'Inquisitor': Params('Инквизитор', 220, dmg=30, arm=5, ini=40, ddg=0, luck=0, mrl=10, mana=7, pwr=30, gold=320, acc=90),
      'Detective': Params('Детектив', 200, 30, 0, 44, 15, 10, 5, 3, 10, 350, 90),
      'DemonLord': Params('Демон-принц', 350, dmg=28, arm=5, ini=30, ddg=0, luck=10, mrl=0, mana=6, pwr=32, gold=0, acc=85),
      'Abbess': Params('Аббатиса', 205, dmg=5, arm=0, ini=30, ddg=5, luck=10, mrl=0, mana=12, pwr=28, gold=380, acc=105),
      'OrcKing': Params('Хан орков', 260, dmg=30, arm=10, ini=38, ddg=0, luck=-37, mrl=-10, mana=0, pwr=0, gold=350, acc=90),
      'Marauder': Params('Мародёр', 210, 24, 0, 56, 0, 8, -10, 7, 25, 430, 95),
      'Archlich': Params('Архилич', 215, dmg=5, arm=5, ini=36, ddg=0, luck=10, mrl=-200, mana=14, pwr=32, gold=400, acc=90),
      'Witch': Params('Ведьмочка', hp=205, dmg=34, arm=0, ini=46, ddg=5, luck=8, mrl=0, mana=12, pwr=28, gold=400, acc=88),

      'GhostWarrior': Params('Воин-призрак', 200, dmg=35, arm=0, ini=15, ddg=15, luck=0, mrl=-200, mana=0, pwr=0, gold=50, acc=95),
      'Specter': Params('Полуденница', hp=180, dmg=0, arm=0, ini=5, ddg=12, luck=0, mrl=-200, mana=0, pwr=25, gold=380, acc=55),
      'Werewolf': Params('Оборотень', 210, 12, 0, 56, 0, 8, -10, 7, 25, 430, 95),
      'Oracle': Params('Оракул эльфов', 180, 0, 0, ini=15, ddg=5, luck=0, mrl=0, mana=6, pwr=30, gold=200, acc=100),
      'Herbalist': Params('Травница', 165, dmg=0, arm=20, ini=10, ddg=5, luck=0, mrl=10, mana=3, pwr=30, gold=400, acc=100), #165
      'Demiurge': Params('Белый маг', hp=200, dmg=0, arm=0, ini=32, ddg=0, luck=10, mrl=0, mana=8, pwr=27, gold=220, acc=90),
      'GoldGolem': Params('Золотой голем', hp=185, dmg=35, arm=25, ini=25, ddg=-20, luck=0, mrl=-200, mana=0, pwr=0, gold=300, acc=95),
      'BeerElemental': Params('Пивной элем-таль', hp=150, dmg=0, arm=0, ini=30, ddg=25, luck=0, mrl=0, mana=0, pwr=0, gold=450, acc=100),
      'Knight': Params('Рыцарь-кентавр', hp=210, dmg=20, arm=15, ini=40, ddg=0, luck=0, mrl=15, mana=0, pwr=0, gold=360, acc=92),
      'Mermaid': Params('Русалка', hp=180, dmg=0, arm=0, ini=48, ddg=0, luck=0, mrl=0, mana=2, pwr=30, gold=290, acc=100),
      'Patriarch': Params('Патриарх', hp=170, dmg=0, arm=5, ini=15, ddg=5, luck=0, mrl=0, mana=12, pwr=25, gold=150, acc=100),
      'Pyro': Params('Гном-пироман', hp=220, dmg=5, arm=10, ini=41, ddg=7, luck=12, mrl=0, mana=2, pwr=18, gold=350, acc=88),
      'EvilTree': Params('Злое дерево', hp=200, dmg=0, arm=10, ini=40, ddg=-5, luck=0, mrl=0, mana=6, pwr=30, gold=320, acc=92),
      'Dracolich': Params('Драколич', 270, dmg=30, arm=15, ini=35, ddg=-15, luck=0, mrl=-200, mana=6, pwr=14, gold=550, acc=75),

      'GoblinTrapper': Params('Гоблин-лучник', 45, 15, 0, 50, 10, 8, -30, 0, 0, 0, 90),
      'GoblinShaman': Params('Гоблин-шаман', 45, 10, 10, 20, 0, 0, 0, 6, 11, 0, 80),
      'Zombie': Params('Зомби', 70, 18, 0, 30, 0, 0, -200, 0, 0, 0, 80),
      'SkeletonChampion': Params('Скелет-чемпион', 120, 30, 15, 50, 0, 15, -200, 0, 0, 0, 85),
      'Ectoplasm': Params('Эктоплазма', 60, 0, 0, 70, 0, 50, 0, 0, pwr=15, gold=0, acc=80),
      'Imp': Params('Толстый бес', 60, 0, 0, 70, 0, 40, 0, 0, pwr=20, gold=0, acc=80),

}

enumOfStatsDict = {key: val for key, val in zip(stats_dict.keys(), range(1, len(stats_dict) + 1))}


PASSIVE_ACTIONS = {
    'Assassin': ('fifthAction', ),
}

DEFEND_OPTIONS = {
    'Assassin': 'гарант крит',
    'Paladin': 'иммун к критам',
    'Inquisitor': 'контрудар',
    'DemonLord': 'лечение',
    'Abbess': 'бафф удачи',
    'OrcKing': 'бафф урона',
    'Marauder': 'гарант укл',
    'Archlich': 'реген оз',
    'Witch': 'бафф точности'
}


COMBAT_MESSAGES = {
    'Assassin': Template('Убийца совершает молниеносный удар кинжалом, нанося $dmg урона, оставляя $hp здоровья.'),
    'Paladin': Template('Один из клинков паладина наносит $dmg урона, оставляя $enemy $hp здоровья.'),
    'Ordinator': Template('Шестопёр инквизитора рассекает воздух и обрушивается на вас, нанося $dmg урона, оставляя $hp здоровья.'),
    'DemonLord': Template('Исполинский витой меч демона-принца вонзается в $enemy, нанося $dmg урона.'),
    'Abbess': Template('Громовое копьё аббатисы бьет с небес и наносит $dmg урона. У $enemy осталось $hp ОЗ.'),
    'OrcKing': Template('Бердыш Хана наносит внушительные $dmg урона. У $enemy осталось $hp ОЗ.'),
    'Marauder': Template('Мародёр выпускает одну стрелу из эльфийского лука, нанося $dmg урона. Осталось $hp ОЗ.'),
    'Archlich': Template('Зелёное облако ядовитых миазмов архилича отнимает у вас $dmg здоровья, оставляя $hp здоровья.'),
    'Witch': Template('Маленькая дрянь неспешно прицеливается из револьвера и стреляет на $dmg урона. У $enemy осталось $hp здоровья...'),
    'GoldGolem': Template('Голем наносит отточенный годами хождений в зал удар на $dmg урона. '),
    'Demiurge': Template('Цепная молния прилетает в $enemy, разряжаясь на $dmg урона. У него осталось $hp здоровья.'),
    'Patriarch': Template('Стена молний проносится по земле, врезаясь в нечестивого $enemy, поджаривая ему ноги на $dmg урона'),
    'Dracolich': Template('Зловонное дыхание дракона отнимает у $enemy $dmg урона, оставляя $hp здоровья.'),
    'EvilTree': Template('Дерево опутывает чёрными корнями беспечного $enemy, высасывая из него жизненные соки на $dmg урона, оставляя $hp здоровья.'),
}




HELPSTRING =\
'Расшифровка иконок: \n 🗡 - атака, 🔰 - броня, 🔮 - сила магии, ⌛- инициатива, 🎯 - точность, ☘ - удача, ⚗ - мана.  💨 уклонение, 💔 - жизни, 🎷 - боевой дух'\
 'Постфикс бывает вида a1 или e1, где a(ally), e(enemy) - указатель на команду - вашу/вражескую, 1 - номер цели в списке команды. Расположение персонажа характеризуется двумя координатами - ' \
 'рядом и колонной. Рядов два - передний и задний, а колонна это номер юнита в данном ряду. Например, боец ближнего боя не способен ударить юнита в дальнем ряду, ' \
'если на переднем ряду вражеской команды кто-то есть. \n'\
 '[исп k], k - номер предмета в инвентаре.'







