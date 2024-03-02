import random
from functools import reduce

from statistics import saveCharsCombinations, processTeamList
from storage.database import write_down_result
from datastore.deffect import EFF
from datastore.dperks import PRK
from ditems.fair import competitive_trade
from imgcreator import create_start_image, makeFieldImage
from myrandom import Chance
from perkchooser import perkMenu
from storage.savegame import saveGame, loadGame
from ditems.usages import useInventory
from utils import isPassive
from vkmodule import send, longpoll, id_checker, send_photo
import varbank as vb
from settings import *
from core import root
from charscreation import creationOfLeaders
from background import HELPSTRING, stats_dict
import copy


def live(members):
    return sorted([x for x in members if x not in vb.done and x not in vb.delayed and x.alive()],
                  key=lambda x: x.ini + random.randint(1, 5), reverse=True) + [unit for unit in vb.delayed[::-1] if unit not in vb.done and unit.alive()]
    # попытка отсортировать пустой список

def getActualMembers(): return sum(vb.teams, [])

def anyoneAliveInTeam(team_number): return any(member.alive() for member in vb.teams[team_number])

def getMember(team, postfix, event):
    try:
        target = vb.teams[team][int(postfix[1]) - 1]
        return target
    except IndexError:
        send(event, f'Был выбран несуществующий персонаж.')
        return -1
    except ValueError:
        return -1

def showStatsOfTeam(team):
    return '\n'.join((member.show_stats(inv=False, effects=True, perks=False, resists=True) for member in vb.teams[team]))

def combat(event, id1, id2, loadFlag=False):
    """
    :param loadFlag: если истина, то массив команды загружается из сохранения.
    :param event:
    :param id1: айди пользователя, который вызвал функцию, написав в ответ на сообщение другого пользователя 'пвп'
    :param id2: тот, которого вызвали на бой.
    :return:
    """
    if loadFlag:
        vb.teams, vb.done, vb.delayed, vb.stage = loadGame()
    else:
        vb.teams = creationOfLeaders(event, id1, id2) if not loadFlag else loadGame()
    vb.archive = copy.deepcopy(vb.teams)
    for member in getActualMembers(): member.startInventory()
    for num in (0, 1):
        vb.Team.Entry(num).gold = round(reduce(lambda acum, y: acum + stats_dict[y.__class__.__name__].gold * GOLD_BONUS, vb.teams[num], 0) * (0.75 if len(vb.teams[num]) > 1 else 1))
    send(event, f'Золото первой команды: {vb.Team.Entry(0).gold}, золото второй: {vb.Team.Entry(1).gold}')
    firstLeader, secondLeader = vb.teams[0][0], vb.teams[1][0]
    if SEND_IMAGES:
        create_start_image(firstLeader, secondLeader)
        send_photo(f'{firstLeader} сойдётся в поединке против {secondLeader}. [справка] Детали интерфейса. \n Да начнётся смертельная битва!', event, 'imgs\\combat.png')
    vb.stage = 1
    while vb.stage < MAX_ROUNDS and anyoneAliveInTeam(0) and anyoneAliveInTeam(1):
        for member in getActualMembers():
            perkMenu(member, event)
            member.effects.timeTicks()
            member.effects.checkEnding()
        while True:
            try:
                unit = live(getActualMembers())[0]
            except IndexError:
                for member in getActualMembers(): member.levelup()
                send(event, f'🎭 Раунд {vb.stage} окончен.')
                vb.stage += 1
                break
            try: print(vb.stage, unit, ' ходит против ', vb.teams[(unit.team + 1) % 2][0])
            except IndexError: pass
            print('Очерёдность хода:', list(map(str, (live(getActualMembers())))))

            if unit not in vb.done:
                turn(event, unit)
                if unit.hasPerk(PRK.LOWHP_EXTRATURN) and Chance(round((1 - (unit.health / unit.max_hp)) * 80)):
                    send(event, f'Стальная воля, железные нервы позволяет сделать {unit.cls_name} еще один ход!')
                    turn(event, unit)
            if Chance(unit.morale) and unit in vb.done:
                unit.rewardForHighMorale()
            print('На ожидании:', list(map(str, vb.delayed)))
            print('Походившие', list(map(str, vb.done)))

        for x in getActualMembers(): x.update()
        vb.delayed.clear()
        vb.done.clear()
        # vb.disabled = []
        if vb.stage % FAIR_FREQUENCY == 0 and anyoneAliveInTeam(0) and anyoneAliveInTeam(1):
            send(event, f'Ярмарка {vb.stage // FAIR_FREQUENCY} начинается!')
            fairLine = sorted([vb.teams[0][0], vb.teams[1][0]], key=lambda y: y.ini + y.gold / 75, reverse=True)
            competitive_trade(*fairLine, event) # fairLine[0], fairLine[1]

    fin_of_battle(firstLeader, secondLeader, vb.stage, event) # Лучше обращаться напрямую к первому элементу, поскольку старый лидер может умереть.




def turn(event, A):
    """
    :param event: обязательный аргумент для функции send()
    :param A: Атакующий игрок
    :return:
    """
    if not A.was_effected: A.effects.applyVOTs(event)
    A.resurrect(event)
    A.psycho(event)
    A.effects.checkEnding() # TODO восстановить, имеет ли смысл проверять?
    A.normalize()
    if A.checkStun(event): return 0
    if A.hasEffect(EFF.SLEEPING):
    # todo но нужно тогда внести параметр previousHealth, который будет хранить здоровье на предыдущем ходу
        send(event, f'{A} сладко спит и пропускает ход. Спи, моя радость, усни.')
        A.sleeping -= 1
        vb.done.append(A)
        return 0
    if A.health <= 0:  # Смерть от дота. Оглушённый и умирающий от дота не воскреснет, если сместить воскрешение под это. Фича?
        return 0
    if not anyoneAliveInTeam((A.team + 1) % 2): # B.death(event) TODO Ранее вызывался death(event) для саммона, его нужно вызывать, но в другом месте.
        vb.done.append(A)
        return 0
    # if isinstance(A, root.Summon) and not isinstance(A, root.Mercenary) and A.master.health <= 0:
    #     # Вот здесь будет проверка для наемников и еще надо будет продолжать партию.
    #     send(event, f'Хозяин погиб, поэтому {A.cls_name} исчезает в небытие, не совершив своего хода.')
    #     vb.done.append(A)
    #     return 0
    if A.not_waited: A.preChoiceAction(vb.teams[(A.team + 1) % 2][0], event)
    send(event, A.show_stats(False, True, False, False) + A.options(vb.teams[(A.team + 1) % 2][0]))
    actionDict = {'1': A.firstAction, '2': A.secondAction, '3': A.thirdAction, '4': A.fourthAction, '5': A.fifthAction}

    for choice in longpoll.listen():
        try:
            current = choice.obj['message']['text'].lower()
        except: # Если кто-то лайкнет фото, то прослушка не обработает
            continue
        if not id_checker(A.id, choice): continue #  and id_checker(A.id, choice)
        match current.split(' '): # todo исп 4 e1 отд 2 a2 инфо 1
            case ['1' | '2' | '3' | '4' | '5'] as text:
                B = vb.teams[(A.team + 1) % 2][0]
                method = actionDict[text[0]]
                if not isPassive(A, method):
                    if B.hasEffect(EFF.INVISIBLE):
                        send(event, f'Вы не можете применить данное действие, поскольку не видите {B}. Он испарился...')
                        continue
                    if B.hasEffect(EFF.SANCTUM):
                        send(event, f'Вы не можете применить данное действие, поскольку {B} защищен мощнейшими охранными чарами.')
                        continue
                    if A.hasEffect(EFF.INVISIBLE):
                        A.effects.delEffect(EFF.INVISIBLE)
                        send(event, f'Вы совершили активное действие - ваша невидимость пропала в тот же миг.')
                if method(B, choice) == -1:
                    send(event, 'Другие действия все ещё доступны.')
                    continue
                else:
                    vb.done.append(A)
                    break
            case ['1' | '2' | '3' | '4' | '5', postfix] as text if len(postfix) == 2 and postfix[0] in ('e', 'a', 'е', 'а'):
                command = text[0]
                team = A.team if postfix[0] in ('a', 'а') else (A.team + 1) % 2
                B = getMember(team, postfix, event)
                if B == -1: continue
                # beginHealthOfB = B.health
                method = actionDict[command]
                if not isPassive(A, method):
                    if B.hasEffect(EFF.INVISIBLE):
                        send(event, f'Вы не можете применить данное действие, поскольку не видите {B}. Он испарился...')
                        continue
                    if B.hasEffect(EFF.SANCTUM):
                        send(event, f'Вы не можете применить данное действие, поскольку {B} защищен мощнейшими охранными чарами.')
                        continue
                    if A.hasEffect(EFF.INVISIBLE):
                        A.effects.delEffect(EFF.INVISIBLE)
                        send(event, f'Вы совершили активное действие - ваша невидимость пропала в тот же миг.')
                if method(B, choice) == -1:
                    continue
                else:
                    vb.done.append(A)
                    break

            case ['w' | 'ц']:
                if A.wait(choice) == -1: continue
                else: break
            case ['инв' | 'i' | 'ш']:
                send(choice, str(A.inv))
                continue
            case ['d' | 'в']:
                if A.protection(choice) == -1:
                    continue
                else:
                    vb.done.append(A)
                    break
            case ['скип']:
                vb.done.append(A)
                break
            case ['t1']:
                send(choice, showStatsOfTeam(A.team))
                continue
            case ['t2']:
                send(choice, showStatsOfTeam((A.team + 1) % 2))
                continue
            case ['поле' | 'f' | 'а']:
                makeFieldImage(vb.teams)
                send_photo(f'Последние донесения, милорд:', event, 'imgs\\field.png')
                continue
            case ['сдаться']:
                send(choice, f'Вы прошли на секретную концовку, поздравляем! {A} сдаётся и покидает поле боя с позором.')
                A.kill()
                vb.done.append(A)
                break
            case ['справка']:
                send(choice, HELPSTRING)
                continue
            case ['m' | 'ь']:
                if not A.movement():
                    send(choice, 'Вы обездвижены или на ряду нет места, поэтому не можете сейчас сменить позицию.')
                    continue
                else:
                    send(choice, f'{A} меняет свою позицию на поле боя.')
                if A.hasPerk(PRK.BONUS_MOVEMENT) and Chance(65):
                    send(choice, f'Благодаря своей расторопности {A} может сделать ещё один ход!')
                    continue
                else:
                    vb.done.append(A)
                    break
            case ['обнов' | 'upd', postfix] if len(postfix) == 2 and postfix[0] in ('e', 'a', 'е', 'а'):
                team = A.team if postfix[0] in ('a', 'а') else (A.team + 1) % 2
                target = getMember(team, postfix, event)
                if target == -1: continue
                send(event, A.options(target))
                continue
            case ['инфо' | 's' | 'ы', postfix] if len(postfix) == 2 and postfix[0] in ('e', 'a', 'е', 'а'): # s - scout.
                team = A.team if postfix[0] in ('a', 'а') else (A.team + 1) % 2
                target = getMember(team, postfix, event)
                if target == -1: continue
                send(event, target.show_stats(inv=False, effects=True, perks=True, resists=True))
                continue
            case ['исп' | 'u', num]:
                # Использование предмета по умолчанию.
                if useInventory(invoker=A, target=A, position=num, ctx=choice) == -1:
                    continue
                else:
                    vb.done.append(A)
                    break
            case ['исп' | 'u', num, postfix] if len(postfix) == 2 and postfix[0] in ('e', 'a', 'е', 'а'):
                # Мы применяем предмет к СОЮЗНИКУ (СЕБЕ). исп 1 а2 - использовать предмет 1 на союзнике под номером 2.
                # Пример: лечащий эликсир. Теперь здоровье будет начисляться target, т.е. тому кто находится в координатах а().
                target = getMember(A.team if postfix[0] in ('a', 'а') else (A.team + 1) % 2, postfix, event)
                if target == -1: continue
                if useInventory(invoker=A, target=target, position=num, ctx=choice) == -1:
                    continue
                else:
                    vb.done.append(A)
                    break
            case ['сохранить']:
                saveGame([vb.teams, vb.done, vb.delayed, vb.stage])
                send(event, 'Игра сохранена!')
                continue
            case ['s' | 'ы']: # line (очередь)
                liveSeq = ', '.join([unit.describe() for unit in live(getActualMembers())])
                delayedSeq = ', '.join([unit.describe() for unit in vb.delayed])
                doneSeq = ', '.join([unit.describe() for unit in vb.done])
                send(event, f'Очерёдность хода: {liveSeq}. \n Подождавшие: {delayedSeq} \n Походившие: {doneSeq}')
                continue
            case ['штраф', num] if num.isdigit():
                send(event, f'"Ох дерьмо, извини", - говорит {A}, предлагая в качестве компенсации {num} золотых. Деньги принимаются, а ваш ход продолжается.')
                vb.Team.Entry(A.team).gold -= int(num)
                vb.Team.Entry(A.enemyTeam).gold += int(num)
                continue
            case _:
                continue
    for unit in getActualMembers():
        if not unit.death(event):
            unit: root.HeroInstance
            if unit.hasEffect(EFF.SLEEPING) and unit.health < unit.previousHealth:
                send(event, f'{unit} просыпается от полученных ран и вступает в бой.')
                unit.effects.delEffect(EFF.SLEEPING)
        unit.previousHealth = unit.health


def fin_of_battle(A, B, stage, event):
    if stage == MAX_ROUNDS:
        send(event, f'#результаты Сражение продлилось {MAX_ROUNDS} раундов, бой остановлен! Ни одна из сторон так и не смогла взять верх. Ничья! ')
        return
    if anyoneAliveInTeam(0) and not anyoneAliveInTeam(1):
        winner, loser = A, B
        winnerTeam = 0
    elif not anyoneAliveInTeam(0) and anyoneAliveInTeam(1):
        winner, loser = B, A
        winnerTeam = 1
    else:
        send(event, '#результаты В этой бойне не было ни победителей, ни проигравших. Оба воина недееспособны - ничья.')
        return
    send(event, f'#результаты Дуэль выиграл [id{str(winner.id)}|{winner.name}]. Состав команды победителя: {reduce(lambda a, x: a + f" {x.cls_name};", vb.archive[winnerTeam], "")}')
    send(event, f'А вам, [id{str(loser.id)}|{loser.name}], надо тренироваться. Состав команды проигравшего: {reduce(lambda a, x: a + f" {x.cls_name};", vb.archive[(winnerTeam + 1) % 2], "")}')
    if RATING_GAME: write_down_result(winner, loser)
    saveCharsCombinations(processTeamList(vb.archive))

    # Внести в таблицу данные об именах победителей и проигравшего, а также об их классах для статистики.
    # if ban_user_if_lose:
    #     send(event, f'Привести приговор в исполнение! Прощайте, {loser.name}.')
    #     vk_session.method("messages.removeChatUser", {"chat_id": event.chat_id, "member_id": loser.id})




