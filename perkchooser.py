# from root import HeroInstance
from datastore.deffect import EFF
from datastore.dperks import PRK, ITEMPERKS
from random import sample
from datastore.dsources import SRC
from core.root import HeroInstance
from vkmodule import send, longpoll, id_checker


# itemPerks = [PRK.AURAS, PRK.TECHNO, PRK.TALISMANS, PRK.ORBS, PRK.SCROLLS, PRK.ARTIFACTS, PRK.STAFFS, PRK.MISC, PRK.MILITARY, PRK.RELICS]
# anotherPerks = [prk for prk in PRK if prk not in itemPerks]

def benefits(unit: HeroInstance, chosenPerk):
    match chosenPerk:
        case PRK.LUCKYBASTARD:
            unit.crit_bank += 1
            unit.dodge_bank += 1
        case PRK.MANDATEOFHEAVEN:
            unit.max_hp = round(1.25 * unit.max_hp)
            unit.heal_rate += 0.25
        case PRK.ARMORPENETRATOR:
            unit.armor_penetration += 0.3
        case PRK.SHINEOFTHISUNGLASSES:
            unit.addEffect(EFF.REFLECTION, 5)
        case PRK.LONGWEAPON:
            unit.lengthOfWeapon += 1
        case PRK.GRAND_MERCHANT:
            unit.merchant += 0.25
        case PRK.MORESUMMONS:
            unit.max_summons += 1
        case PRK.SIGMALIKE:
            unit.resists[SRC.STUN].changeValue(40)
        case _:
            pass


def perkMenu(unit, ctx):
    if unit.isSummon: return 0
    if unit.health <= 0 and unit.lives <= 0: return 0
    if not unit.hidden_lvl % unit.develop == 0: return 0 # еще было требование unit.hidden_lvl > 0, но пока не знаю что я имел в виду.
    anotherPerks = [prk for prk in PRK if prk not in ITEMPERKS]
    mySample = sample(ITEMPERKS, 4) + sample(anotherPerks, 2)
    report = f''
    for i, elem in enumerate(mySample):
        report += f'{i+1}. {elem.value[0]}: {elem.value[1]} {"⛔" if unit.hasPerk(elem) else "✅"}\n'
    send(ctx, f'{unit}, вы заслужили выбрать перк. Укажите номер интересующей вас способности. \n [скип] - Пропустить вкуснейший выбор, получить бонусный уровень. ')
    send(ctx, report)
    send(ctx, str(unit.inv))
    for choice in longpoll.listen():
        try: current = choice.obj['message']['text'].lower()
        except: continue
        if not id_checker(unit.id, choice): continue
        match current:
            case '1' | '2' | '3' | '4' | '5' | '6' as num: # TODO ХАРДКОДИНГ ЗАВЯЗАНО НА КОЛИЧЕСТВЕ ПРЕДЛАГАЕМЫХ ПЕРКОВ
               if mySample[int(num) - 1] in unit.skills:
                   send(ctx, 'Вы уже знаете этот перк!')
                   continue
               chosenPerk = mySample[int(num) - 1]
               unit.skills.append(chosenPerk)
               benefits(unit, chosenPerk)
               send(ctx, f'Поздравим же {unit} c изучением перка {chosenPerk.value[0]}!')
               break
            case 'скип':
                send(ctx, 'Зануда 👺!')
                unit.levelup()
                break
            case _:
                continue



