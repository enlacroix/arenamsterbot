from random import choice

from characters.dragon import Dracolich
from vkmodule import send, get_first_name, longpoll, id_checker, send_photo, sendSeveralPhoto

from characters.beerelem import BeerElemental
from characters.eviltree import EvilTree
from characters.ghwarrior import GhostWarrior
from characters.golem import GoldGolem
from characters.herbalist import Herbalist
from characters.knight import Knight
from characters.mermaid import Mermaid
from characters.oracle import Oracle
from characters.patriarch import Patriarch
from characters.demiurge import Demiurge
from characters.pyro import Pyro
from characters.specter import Specter
from characters.assasin import Assassin
from characters.inquisitor import Inquisitor
from characters.demonlord import DemonLord
from characters.detective import Detective
from characters.lich import Archlich
from characters.orc import OrcKing
from characters.witch import Witch
from characters.paladin import Paladin
from characters.abbess import Abbess
from characters.marauder_werewolf import Marauder
from settings import *

# Сочетание ключи-персонажи в соответствии с тем, как они указаны на вступительной картинке.
PICKING_CHARS = {1: Assassin,
                 2: Paladin,
                 3: Inquisitor,
                 4: Detective,
                 5: DemonLord,
                 6: Abbess,
                 7: OrcKing,
                 8: Marauder,
                 9: Archlich,
                 10: Witch,
                 11: GhostWarrior,
                 12: Specter,
                 13: Oracle,
                 14: Herbalist,
                 15: Demiurge,
                 16: GoldGolem,
                 17: BeerElemental,
                 18: Knight,
                 19: Mermaid,
                 20: Patriarch,
                 21: Pyro,
                 22: EvilTree,
                 23: Dracolich
                 }


# for pick in longpoll.listen():
#     try:
#         current = pick.obj['message']['text'].lower()
#     except KeyError | ValueError: continue
#     match current.split(' '):
#         case ['слайд', n] as command if int(n) in range(1, 4 + 1):
#             send_photo(' ', event, f'imgs\\intro\\intro{int(n)}.jpg')

def creationOfLeaders(event, id1, id2) -> list[list, list]:
    if DEVMODE: return [[DemonLord(id1)], [Inquisitor(id2)]] # , Assassin(id1) , Assassin(id2)
    paths = []
    if SEND_IMAGES:
        for i in range(1, 5): paths.append(f'imgs\\intro\\intro{i}.jpg')
        sendSeveralPhoto(' ', event, paths)
        # for i in range(1, 5):
        #     send_photo(' ', event, f'imgs\\intro\\intro{i}.jpg')
        send(event, INTROMessage2)
    else: send(event, INTROMessage)

    res = [[], []]
    send(event, f'Размер команды на старте: {INITIAL_TEAM_SIZE}. \n'
                f'Максимальный размер команды: {MAX_TEAM_SIZE}. ')
    send(event, f'Команды поочерёдно выбирают персонажей. \n'
                f'Напишите номер выбранного героя или [случ] - случайный класс. '
                f'Чтобы поставить юнита в задний ряд, добавь постфикс [зр] или [br] через пробел. [4 зр] - пример.')
    while True:
        if canPickOnceMore(res, 0):
            send(event, f'Выбирает {get_first_name(id1)}:')
            res[0].append(askAboutClass(event, id1, res[0]))
        if canPickOnceMore(res, 1):
            send(event, f'Выбирает {get_first_name(id2)}:')
            res[1].append(askAboutClass(event, id2, res[1]))
        if not(canPickOnceMore(res, 0) or canPickOnceMore(res, 1)):
            send(event, 'Выбор персонажей окончен, спасибо.')
            break
    return res

def canPickOnceMore(res, team_number) -> bool:
    return sum([x.size for x in res[team_number]]) < INITIAL_TEAM_SIZE


def randomPickOfHero(event, _id):
    X = choice(list(PICKING_CHARS.values()))(_id)
    send(event, f'{X.name}, да вы оказывается {X.cls_name}!')
    return X


def askAboutClass(event, _id, charList):
    for pick in longpoll.listen():
        try:
            current = pick.obj['message']['text'].lower()
        except KeyError | ValueError: continue
        if not id_checker(_id, pick): continue
        match current.split(' '):
            case [n] | [n, 'зр' | 'br'] as command if n in map(str, range(1, len(PICKING_CHARS) + 1)):
                hero = PICKING_CHARS[int(n)](_id)
                assumingPosition = 1 if command[-1] in ('зр', 'br') else 0
                heroSize = PICKING_CHARS[int(n)].size
                sumOfSizes = sum([x.size for x in charList])
                if sumOfSizes + heroSize > INITIAL_TEAM_SIZE:
                    send(event, 'У вас нет места в отряде для данного героя. Пожалуйста, выберите другого.')
                    continue
                if len(tuple(filter(lambda x: x.position == assumingPosition, charList))) + 1 > MAX_ROW_SIZE:
                    send(event, f'На этом ряду нет места, нужно выбрать другой.')
                    continue
                hero.position = assumingPosition
                send(event, f'Прекрасный выбор. В отряд {get_first_name(_id)} вступает {hero.cls_name}.')
                return hero
            case ['случ' | 'rand'] | ['случ' | 'rand', 'зр' | 'br'] as command:
                hero = randomPickOfHero(event, _id)
                assumingPosition = 1 if command[-1] in ('зр', 'br') else 0
                heroSize = hero.__class__.size
                sumOfSizes = sum([x.size for x in charList])
                if sumOfSizes + heroSize > INITIAL_TEAM_SIZE:
                    send(event, 'У вас нет места в отряде для данного героя. Пожалуйста, выберите другого.')
                    continue
                if len(tuple(filter(lambda x: x.position == assumingPosition, charList))) + 1 > MAX_ROW_SIZE:
                    send(event, f'На этом ряду нет места, нужно выбрать другой.')
                    continue
                hero.position = assumingPosition
                return hero
            case _:
                continue



