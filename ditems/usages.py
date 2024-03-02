from random import randint, choice

from characters.assasin import Assassin
from characters.beerelem import BeerElemental
from characters.eviltree import EvilTree
from characters.ghwarrior import GhostWarrior
from characters.golem import GoldGolem
from characters.herbalist import Herbalist
from characters.mermaid import Mermaid
from characters.oracle import Oracle
from characters.pyro import Pyro
from characters.specter import Specter
from datastore.deffect import EFF
from datastore.dperks import PRK, PerkCategoryDict
from datastore.dsources import SRC
from datastore.misc import RACES
from ditems.itemcls import Item
from myrandom import Chance
from core.root import HeroInstance
from vkmodule import send, longpoll, id_checker
import summon_classes.goblins
import summon_classes.another
import summon_classes.undeads
import varbank as vb

# def giveItemToAlly(unit, target, position, ctx):
#     item = unit.inv.getItem(position)
#     if item is None:
#         send(ctx, f'Предмета с номером {position} не существует в инвентаре.')
#         return -1
#     unit.inv.removeItem(item)
#     target.inv.addItem(item)
#     send(ctx, f'{unit} украдкой передаёт {item.name} надежному {target}.')
#     return 1

def useInventory(invoker: HeroInstance, target: HeroInstance, position: str, ctx):
    """
    (действие: использовать первый предмет)
    u 1: действие на себя. invoker=target
    u 1 a1: действие на союзника. invoker=A
    u 1 e1: действие на врага. invoker=A
    :param invoker:
    :param target:
    :param position:
    :param ctx:
    :return:
    """
    item = invoker.inv.getItem(int(position))
    if item is None:
        send(ctx, f'Предмета с номером {position} не существует в инвентаре.')
        return -1
    if not item.isAble(invoker):
        send(ctx, f'У {invoker} нет навыка {PerkCategoryDict[item.category].value[0]} для использования {item.name}.')
        return -1
    res = usage(item.code, target, invoker, ctx)
    item.generalUseItem(res, invoker)
    if res not in (0, -1) and invoker.hasPerk(PRK.DOUBLE_USING_INVENTORY) and Chance(50):
        send(ctx, 'Перк на быструю упаковку позволяет сделать еще один ход!')
        return -1
    return res




def usage(code: int, target: HeroInstance, invoker: HeroInstance, ctx):
    """
    :return: 1 - стандартное использование, 0 - предмет не удаляется из инвентаря, -1 - даёт ход после применения
    """
    match code:
        # АУРЫ.
        # case 300:
        #     if A.team == B.team:
        #         send(ctx, f'{B} должен быть вашим врагом.')
        #         return -1
        #     A.crit += 20
        #     B.crit += 20
        #     send(ctx, 'Здорово! +20 Удачи вам. Ну и вашему противнику тоже.')
        #     return 1
        # case 410:
        #     if A.team == B.team:
        #         send(ctx, f'{B} должен быть вашим врагом.')
        #         return -1
        #     A.crit -= 30 + A.lvl
        #     B.crit -= 30 + A.lvl
        #     send(ctx, f'Сегодня у всех неудачный день. {30 + A.lvl} удачи потеряно безвозвратно для {A.cls_name} и {B.cls_name}.')
        #     return 1
        # case 470:
        #     if A.team == B.team:
        #         send(ctx, f'{B} должен быть вашим врагом.')
        #         return -1
        #     if A.arm < 45:
        #         send(ctx, f'{A} - внимательно на условия применения ауры.')
        #         return -1
        #     A.arm = 0
        #     B.arm = 0
        #     send(ctx, f'Настало время честной, первобытной драки - клинок на клинок!')
        #     return 1
        # case 330:
        #     if A.team == B.team:
        #         send(ctx, f'{B} должен быть вашим врагом.')
        #         return -1
        #     A.heal(50 + A.lvl * 7)
        #     B.heal(50)
        #     send(ctx, f'Вжух.')
        #     return 1
        # case 400:
        #     if A.team == B.team:
        #         send(ctx, f'{B} должен быть вашим врагом.')
        #         return -1
        #     A.inv.removeItem(Item(400))
        #     for inventory in [A.inv, B.inv]:
        #         for item in inventory:
        #             inventory.pool[item] += 1
        #     send(ctx, 'Аура дублирует предметы в инвентарях соперников.')
        #     return 0
        # case 340:
        #     if A.team == B.team:
        #         send(ctx, f'{B} должен быть вашим врагом.')
        #         return -1
        #     A.gold //= 2
        #     B.gold //= 2
        #     A.inv.addItem(Item(137))
        #     send(ctx, f'Аура уничтожила половину капиталов обоих лидеров - золото почернело и обратилось в пыль. Но вы чувствуете, как в вашем кармане очутилась какая-то бумага.'
        #               f'Возможно это награда за ваш Смелый и Бунтарский поступок.')
        #     return 1
        # case 520:
        #     if A.team == B.team:
        #         send(ctx, f'{B} должен быть вашим врагом.')
        #         return -1
        #     A.mana = -3
        #     B.mana = -3
        #     send(ctx, 'Аура поглощает магическое поле, уничтожая ману обеих игроков.')
        #     return 1

        # Талисманы
        case 541:
            if target.createSummon(summon_classes.goblins.GoblinTrapper, ctx):
                send(ctx, f'С помощью талисмана вы призываете гоблина-налётчика, шалопая окаянного.')
                return 1
            return -1
        case 411:
            if target.lvl <= 5:
                if target.createSummon(summon_classes.undeads.Zombie, ctx):
                    send(ctx, f'Обычный зомби откликается на зов вашего талисмана.')
                    return 1
                return -1
            if 6 <= target.lvl <= 11:
                if target.createSummon(summon_classes.undeads.SkeletonChampion, ctx):
                    send(ctx, f'Ваше возросшее могущество позволило вам призвать скелета-чемпиона.')
                    return 1
                return -1
            if target.lvl >= 12:
                if target.createSummon(GhostWarrior, ctx):
                    send(ctx, f'Хвалю ваше терпение, мой юный некромант. Теперь на зов вашего талисмана откликнутся воин-призрак.')
                    return 1
                return -1
        case 741:
            if target.createSummon(EvilTree, ctx):
                send(ctx, f'Упырица вступает в бой...')
                return 1
            return -1
        case 751:
            if target.createSummon(Assassin, ctx):
                send(ctx, f'')
                target.summons[-1].dnote = 20
                return 1
            return -1
        case 651:
            if target.createSummon(Mermaid, ctx):
                send(ctx, 'Ближайшая лужа разливается в прекрасное озеро, из которого выходит Русалка на зов вашего Талисмана.')
                return 1
            return -1
        case 701:
            if target.createSummon(Pyro, ctx):
                send(ctx, 'Из клубов пара и гари появляется гном-кузнец-огнемётчик-филантроп и многодетный отец. Из одежды на нем только фартук.')
                return 1
            return -1
        case 321:
            if target.createSummon(summon_classes.another.Ectoplasm, ctx):
                send(ctx, 'Вы призываете нестабильную эктоплазму, который сбежал из лабораторий чернокнижников.')
                return 1
            return -1
        case 431:
            if target.createSummon(summon_classes.goblins.GoblinShaman, ctx):
                send(ctx, 'Перед вами материализуется заспанный шаман гоблинов, готовый вам служить, повелитель.')
                return 1
            return -1
        case 521:
            if target.createSummon(Oracle, ctx):
                send(ctx, 'Силами талисмана вы призываете эльфийку-оракула.')
                return 1
            return -1
        case 601:
            if target.createSummon(Herbalist, ctx):
                send(ctx, 'Силами талисмана вы призываете травницу.')
                return 1
            return -1
        case 581:
            if target.createSummon(Specter, ctx):
                send(ctx, 'Силами талисмана вы призываете ужасного призрака.')
                return 1
            return -1

        # Технологии
        case 322:
            for enemy in target.getOwnRow():
                enemy.health -= randint(40, 60)
            send(ctx, f'Картечь разлетается во все стороны, калеча вражескую команду примерно на 40-60 здоровья.')
            return 1
        case 532:
            if target.evade(target, 0, ctx):
                return 0
            target.health -= 30 + target.lvl * 2
            send(ctx, f'Ружье взведено, нервы напряжены - вы нанесли {30 + target.lvl * 2} урона!')
            if Chance(target.lvl * 10):
                return 0
            else:
                send(ctx, f'Вы не проявили должного навыка и впустую растратили все патроны. Мушкет теперь бесполезен, и вы его выкинули от злости в кусты.')
                return 1
        case 932:
            target.health -= 75 + target.lvl * 2
            send(ctx, f'Внеземной бластер Чужих (о как же он прекрасен и лорен) выпускает сгусток плазмы, наносящей {75 + target.lvl * 2} урона.')
            return 0
        case 762:
            target.race = RACES.ARTIFICIAL
            send(ctx, f'Парень из толпы показался вам отличным хирургом, и он был приглашён на операцию по вживлению вам механического сердца, которое сделает из вас '
                      f'бездушное порождение технологий. Вы больше никогда не сможете улыбнуться, порадоваться или сострадать. Но вы и не сойдёте с ума и не умрёте от сердечного приступа. ')
            return 1
        case 522:
            for eff in target.effects.pool:
                if eff.canRemove and not eff.isPositive: eff.rounds = 0
            send(ctx, f'Аптечка Древних специальными манипуляторами очистила ваш организм и восстановила {target.heal(200)} здоровья.')
            return 1
        case 662:
            send(ctx, '«Молвят, ведьмак собьёт стрелу на лету»... В этих стильных очках оказалась еще и встроенная система наведения и GPS-навигатор.')
            target.acc += 40 + target.lvl
            return 1
        case 562:
            send(ctx, 'В инжекторном пистолете содержался дротик с веществом, которое способно подавить метаболизм в теле человека.')
            target.heal_rate -= 0.25
            return 1
        case 402:
            target.resists[SRC.STUN].changeValue(50)
            send(ctx, 'Нейроусилитель делает вас практически неуязвимым к беспардонным попыткам вас оглушить.')
            return 1
        case 412:
            target.addEffect(EFF.FIREDWEAPON, 3)
            send(ctx, f'Вы смазываете своё оружие огненной смолой - удивительным подарком забытой цивилизации.')
            return 1
        case 572:
            if target.createSummon(GoldGolem, ctx):
                send(ctx, 'Поколдовав с отверткой и покурив пару-тройку гайдов, вы вводите Голема в эксплуатацию.')
                return 1
            return -1

        # Сферы
        case 513:
            summon_bank = [Oracle, Herbalist, Mermaid]
            target.transformToAnotherClass(choice(summon_bank))
            send(ctx, 'Красотища.')
            return 1
        case 523:

            send(ctx, f'Хищно улыбаясь, вы подходите к несчастному {target}. Он дрожит от страха, но не в состоянии изменить свою участь. Вы разбиваете сферу об его голову.'
                 f'Газ, содержащийся в ней, медленно расправляется с {target}, пока он орёт от боли. Отныне он Призрак, но он никогда вам этого не забудет.')
            vb.teams[target.team].append(Specter(target.id))
            target.kill()
            return 1
        case 613:
            if not target in vb.done:
                send(ctx, f'Дождитесь пока {target} сделает свой ход, иначе магия пропадёт впустую.')
                return 0
            vb.done.remove(target)
            send(ctx, f'{target} получает дополнительный ход.')
            return 1
        case 363:
            for eff in target.effects.pool:
                if eff.canRemove and eff.isPositive: eff.rounds = 0
            send(ctx, f'Положительные эффекты спали и сфера нанесла {target.harmWithSRC(SRC.WATER, 60)} урона.')
            return 1
        case 433:
            target.dmg = round(target.dmg * 0.7)
            send(ctx, f'Сфера ослабляет физический урон противника на 30%, теперь противник имеет {target.dmg} пт урона.')
            return 1
        case 233:
            target.develop += 3
            send(ctx, 'Сфера замедлила процесс получения перков противником. К сфере прилагается записка - "Кто её применит - тот клоун 🤡". Мораль думай сам.')
            return 1
        case 413:
            for x in vb.teams[target.team]: x.levelup(2)
            send(ctx, f'Разбив сферу об пол, вы убедились что в ней содержался целый тюбик мельдония. Вот тебе чародейство и волшебство...')
            return 1
        case 323:
            target.health = round(target.health * 0.7)
            send(ctx, f'Сфера мучительно перестраивает ваше тело изнутри, причиняя жуткую боль. Вы потеряли {round(target.health * 0.3)} здоровья.')
            return 1
        case 353:
            if target.morale >= 0 or target.morale < -150:
                send(ctx, f'Сфера не подействует, поскольку у вас неправильный боевой дух.')
                return -1
            send(ctx, f'Все ваши страдания, боль, унижения конвертировались в {target.harmWithSRC(SRC.MIND, abs(target.morale) * 2.5)} урона по противнику.')
            return 1
        case 343:
            if Chance(100, SRC.MIND).roll(target):
                send(ctx, 'Вы разбиваете сферу, из которой слышны крики баньши. Они идут за тобой...')
                target.addEffect(EFF.STUNNED, 1)
            else:
                send(ctx, 'Оппонент не поддается влиянию сферы.')
            return 1

        # Свитки
        case 354:
            target.resists[SRC.FIRE].changeValue(-(20 + target.lvl))
            target.resists[SRC.DEATH].changeValue(-(20 + target.lvl))
            send(ctx, f'Свиток уменьшает сопротивление врага к Огню и Смерти на {20 + target.lvl}%.')
            return -1 if Chance(50) else 1
        case 334:
            target.resists[SRC.AIR].changeValue(-(20 + target.lvl))
            target.resists[SRC.MIND].changeValue(-(20 + target.lvl))
            send(ctx, f'Свиток уменьшает сопротивление врага к Воздуху и Разуму на {20 + target.lvl}%.')
            return -1 if Chance(50) else 1
        case 444:
            n = len(target.inv)
            if n == 0:
                send(ctx, 'Инвентарь противника пуст.')
                return -1
            item = target.inv.getItem(randint(1, n))
            target.inv.removeItem(item)
            report = f'Свиток уничтожил предметы: {item}'
            if len(target.inv) > 0:
                item2 = target.inv.getItem(randint(1, n))
                target.inv.removeItem(item2)
                report += f' и {item2}!'
            send(ctx, report)
            return 1
        case 454:
            target.levelup(-3)
            if len(target.skills) > 0:
                x = choice(target.skills)
                target.skills.remove(x)
            send(ctx, f'Дрожащими руками {target} разворачивает свиток, в котором содержится заказ на 24-часовой марафон на просмотр аниме "Бесконечная восьмёрка". Приятного просмотра!')
            return 1
        case 474:
            send(ctx, f'Доспех укреплён на {15 + target.lvl * 3} пт. Также незерит защитит вас от первой физической атаки.')
            target.arm += 15 + target.lvl * 3
            target.resists[SRC.WEAPON].setWard()
            return -1 if Chance(50) else 1
        case 434:
            target.max_hp //= 2
            send(ctx, 'Свиток лишает вас врождённого здоровья. Ваше максимальное здоровье уменьшено в два раза.')
            return 1
        case 404:
            target.health -= target.mana * 10
            send(ctx, f'Свиток наносит {target.mana * 10} урона Жизнью, пожирая {target.mana // 2} единиц маны.')
            target.mana //= 2
            return 1

        # Реликвии
        case 475:
            if not target.isSummon:
                send(ctx, 'Выбранная цель не является саммоном.')
                return -1
            if not target.race in (RACES.UNDEAD, RACES.DEMON):
                send(ctx, 'Цель не является демоном или нежитью.')
                return -1
            target.health -= 100
            send(ctx, f'Вы облили мерзкого {target} святой водой. Изыди, сволочь!')
            return 1
        case 935:
            target.lives += 3
            send(ctx, 'Ознакомившись с учением пророка Изатиса, вы постигли и смирились со своим Уделом страдать. Зато вы стали ближе к Богам и получили три дополнительных Жизни.')
            return 1
        case 715:
            if not target.isSummon:
                send(ctx, 'Тебе это не нужно...')
                return -1
            target.isMercenary = True
            send(ctx, f'Духовные оковы не позволят саммону сбежать с поля боя: он будет сражаться до конца и сможет завершить начатое вами.')
            return 1
        case 315:
            target.resists[SRC.HOLY].setWard()
            target.resists[SRC.HOLY].changeValue(20)
            send(ctx, f'Сила епископской печати убережёт вас от нападок настоящих служителей Церкви.')
            return 1
        case 325:
            send(ctx, f'Знания, изложенные в древнем фолианте, оказываются крайне полезными (да тут еще и картинки есть!). Вы поднимаете три уровня разом.')
            target.levelup(3)
            return 1
        case 555:
            currList = [PRK.AURAS, PRK.TALISMANS, PRK.TECHNO, PRK.ORBS, PRK.SCROLLS, PRK.RELICS, PRK.ARTIFACTS, PRK.MISC, PRK.STAFFS, PRK.MILITARY]
            send(ctx, f'Теперь вы владеете всеми необходимыми перками для использования предметов.')
            target.skills += [x for x in currList if x not in target.skills]
            return 1

        case 655:
            report = f'[0]. Выйти из меню. \n'
            N = len(vb.Team.Entry(target.team).graveyard)
            for i, unit in enumerate(vb.Team.Entry(target.team).graveyard):
                report += f'{i + 1}. {unit}, уровень {unit.lvl}, {"🚫" if unit.isForbiddenToResurrect else "✅"} \n'
            send(ctx, report)
            for event in longpoll.listen():
                if not id_checker(target.id, ctx): continue
                current: str = event.obj['message']['text'].lower()
                if current == '0': break
                if current.isdigit() and int(current) <= N:
                    target: HeroInstance = vb.Team.Entry(target.team).graveyard[int(current) - 1]
                    if not target.animate(target.team):
                        send(ctx, 'Цель невозможно поднять, так как она была подвержена проклятью искоренения.')
                        continue
                    else:
                        send(ctx, f'{target} успешно восстал из мёртвых!')
                        if Chance(50): target.isForbiddenToResurrect = True
                        break
            return 1
        case 665:
            target.max_hp = round(1.5 * target.max_hp)
            send(ctx, f'Максимальное здоровье было увеличено на 50%, а текущее было восстановлено на {target.heal(target.health // 2)} пт.')
            return 1
        case 355:
            target.arm += 20
            target.skills.append(PRK.BONUS_MOVEMENT)
            send(ctx, 'Отличные сапоги, надо брать.')
            return 1
        case 465:
            send(ctx, 'Вы одаряете себя великой силой Создателя и Творца')
            target.skills.append(PRK.SUMMON_LEVEL_UP)
            return 1

        # Артефакты
        case 346:
            send(ctx, 'Надев на себя шлем-диадему, вы ощущаете прикосновение источника магической энергии...')
            target.resists[SRC.MIND].changeValue(20)
            target.addEffect(EFF.REGENMANA, 4, power=[2])
            return 1
        case 476:
            target.resists[SRC.FIRE].changeValue(15)
            target.resists[SRC.DEATH].changeValue(15)
            target.arm += 50
            send(ctx, 'Латы дают вам 50 брони и сопротивления.')
            return 1
        case 216:
            target.power = round(0.7 * target.power)
            send(ctx, f'Амулет уничтожает часть могущества {target}.')
            return 1
        case 516:
            target.heal_rate += 0.25
            send(ctx, 'Перчатки рыцаря Вереска делают вас нежным и чувствительным.')
            return 1
        case 406:
            target.mana, target.mana = target.mana, target.mana
            send(ctx, f'Вы обмениваетесь значениями маны.')
            return 1
        case 456:
            target.ini += 20 + target.lvl
            send(ctx, f'Вы чувствуете, что мы можем немного ускориться! Ваша инициатива поднята на {20 + target.lvl} пт.')
            return 1
        case 736:
            target.arm = 80
            target.resists[SRC.DESTROYARMOR].setImmunity()
            send(ctx, f'Латы Титана невероятно прочны, но громоздки - все предыдущие одежды пришлось снять.')
            return 1
        case 466:
            target.addEffect(EFF.KILLMANA, 3, power=[3])
            send(ctx, f'Оковы защелкиваются на руках вражеского мага, зажигаясь синим цветом.')
            return 1
        case 576:
            send(ctx, f'[ЭНЦИКЛОПЕДИЯ][Бесполезно-Успех!] Прославленный царь минотавров, Ксеркс I Солнцеподобный, был также знаменит за упорную борьбу с лже-воскрешением.')
            target.lives -= 2
            target.isForbiddenToResurrect = True
            return 1
        case 566:
            send(ctx, f'{target} получает дополнительную жизнь.')
            target.lives += 1
            return 1
        case 616:
            send(ctx, f'{target} надевает удобные сапоги Ордена, и чувствует как он крепче стоит на ногах.')
            target.resists[SRC.FINALSTRIKE].changeValue(75)
            return 1
        case 276:
            send(ctx, f'Удача оппонента снижена на {12 + target.lvl * 2} пунктов.')
            target.crit -= 12 + target.lvl * 2
            return 1
        case 636:
            send(ctx, 'Королевские грифоны Эрафии известны тем, что они отвечают на любую провокацию. Теперь это свойство передалось и вам.')
            target.addEffect(EFF.CONTR, 4)
            return 1
        case 646:
            send(ctx, 'Чалма султана-ифрита отлично сидит на вашей голове, окружая вас огненным барьером.')
            target.addEffect(EFF.FIRESHIELD, 4)
            return 1
        case 906:
            send(ctx, 'Камень, упавший с небес, один из символов Императорской династии, обладает силой защищать своего владельца от любых невзгод. '
                      'Остается только понять, что он делает на этой сомнительной ярмарке.')
            for src in SRC:
                target.resists[src].changeValue(50)
            return 1
        case 246:
            target.power += target.lvl + 14
            send(ctx, f'Кристалл усиливает вашу магию на {target.lvl + 14} единиц.')
            return 1
        case 356:
            target.crit_bank += 2
            target.dodge_bank += 2
            send(ctx, f'ВЫ ВЫБРАЛИ НЕПРАВИЛЬНОГО БОСМЕРА! Вы чувствуете истинную пустотелость.')
            return 1

        # Расходники.
        case 107:
            value = round((1.5 if target.hasEffect(EFF.POISON) else 1) * (20 + target.lvl))
            target.health -= value
            send(ctx, f'Метательный нож убийцы нанес {value} урона.')
            return 1
        case 217:
            send(ctx, f'Не годится для употребления. Лучше продать.')
            return -1
        case 317:
            target.dmg += max(0, target.arm // 2)
            target.arm = 0
            send(ctx, 'Мёд админа крепко вдарил вам в голову! Вы раздеваетесь и чувствуете себя сильным и свободным.')
            return 1
        case 367:
            target.addEffect(EFF.IMAGINARYHEALTH, 3, power=[120])
            send(ctx, f'Выпив эликсир, вы ощущаете прилив сил. Но эти силы покинут вас, ровно в то же мгновение, когда кончится эффект.')
            return 1
        case 477:
            send(ctx, 'Вы крутите в руках драгоценный камень, который оказался в вашей сумке. Что ж, её можно выгодно продать ювелиру. ')
            return -1
        case 137:
            send(ctx, 'Свежеотпечанная акция сомнительной фирмы-однодневки. Годится только для моментальной продажи.')
            return -1
        case 297:
            target.resists[SRC.DESTROYARMOR].setWard(3)
            send(ctx, f'Вы щедро заливаете в сочленения своего доспеха купленное зелье. Должно сработать. Наверное.')
            return 1
        case 357:
            target.develop -= 3
            target.levelup(-1)
            send(ctx, f'Это было тяжело, но вы справились. Омерзительный почерк, грязные исправления, матерные стишки на полях, но вы преисполнились мудростью автора'
                      f' - вы будете получать перки чаще.')
            return 1
        case 197:
            send(ctx, f'Боевой дух оппонента снижен на {20 + target.lvl} пунктов.')
            target.morale -= 20 + target.lvl
            return 1
        case 337:
            send(ctx, f'Вы облились парфюмом с ног до головы, чтоб наверняка поразить работников ярмарки. Теперь вы пахнете сиренью и крыжовником.')
            target.merchant += 0.25
            return 1
        case 207:
            send(ctx, f'Снюхав жирную дорожку сахара, вы обрели {12 + target.lvl}% шансов критического удара.')
            target.crit += 12 + target.lvl
            if Chance(2):
                target.kill()
                send(ctx, 'Но вы умерли от сердечного приступа.')
            return 1
        case 407:
            target.crit_bank += 2
            target.ini += 10
            if Chance(4):
                target.kill()
                send(ctx, 'Но вы умерли от сердечного приступа.')
            return 1
        case 187:
            send(ctx, f'Ваша броня увеличена на {16 + target.lvl * 2} пт.')
            target.arm += 16 + target.lvl * 2
            return 1
        case 397:
            send(ctx, f'Вы временно усилили свой урон на 50%.')
            target.addEffect(EFF.STRENGTH, 3, power=[0.5])
            return 1
        case 237:
            send(ctx, f'Ваше здоровье восстановлено на {target.heal(75)} пт.')
            return 1
        case 387:
            send(ctx, f'Ваше здоровье восстановлено на {target.heal(150)} пт. Прекрасное средство, не так ли?')
            return 1
        case 2137:
            target.addEffect(EFF.STONEFLESH, 3, power=[25])
            target.addEffect(EFF.REGENHP, 3, power=[1.25])
            send(ctx, f'вкусно.')
            return 1
        case 2187:
            target.dmg += 12 + target.lvl + target.lvl // 2
            target.addEffect(EFF.DRUNK, randint(2, 3), power=[25])
            send(ctx, f'Отвратительное пойло! Какие малютки вообще могут пить подобное? Вы жутко пьяны, но +{12 + target.lvl + target.lvl // 2} атаки, есть +{12 + target.lvl + target.lvl // 2} атаки.')
            return 1
        case 267:
            target.effects.delEffect(EFF.FEAR)
            target.resists[SRC.MIND].setWard()
            send(ctx, 'Настойка успокоила ваши нервы и обволокла разум.')
            return 1
        case 147:
            x = randint(3, 4)
            send(ctx, f'Магия восстановлена на {x} пунктов.')
            target.mana += x
            return 1
        case 307:
            x = randint(6, 9)
            send(ctx, f'Магия восстановлена на {x} пунктов.')
            target.mana += x
            return 1
        case 227:
            send(ctx, f'Намазавшись атлетическим маслом, вы способны выскользнуть из-под любой атаки. Уклонение увеличено на {10 + target.lvl} пт.')
            target.dodge += 10 + target.lvl
            return 1
        case 287:
            target.effects.delEffect(EFF.POISON)
            target.resists[SRC.DEATH].setWard()
            send(ctx, 'Противоядие очистило ваш организм.')
            return 1
        case 117:
            beer = 18 + target.lvl if target.morale < 0 else 12
            target.morale += beer
            send(ctx, f'Реклама не врала, вы ощущаете приятное фруктовое послевкусие. А жизнь-то налаживается! Ваш боевой дух поднят на {beer} единиц.')
            return 1
        case 247:
            send(ctx, 'Очень по-взрослому. Но сделанного не воротишь - ваш противник отравлен.')
            target.addEffect(EFF.POISON, 4, power=[1.1])
            return 1
        case 167:
            target.addRandItemsByTier(infimum=3, supremum=4, count=1)
            send(ctx, 'Определённо это кейс нового тысячелетия.')
            return -1 if target.hasPerk(PRK.LUDOMANIA) else 1
        case 447:
            target.addRandItemsByTier(infimum=5, supremum=6, count=1)
            send(ctx, 'Ого! Ничего себе! Просто вау. Беги смотреть!')
            return -1 if target.hasPerk(PRK.LUDOMANIA) else 1
        case 647:
            target.addRandItemsByTier(infimum=7, supremum=8, count=1)
            send(ctx, f'Невероятная вещица сегодня выпадает нам, дорогие друзья! Вкуснятина.')
            return -1 if target.hasPerk(PRK.LUDOMANIA) else 1
        case 747:
            target.addRandItemsByTier(infimum=9, supremum=9, count=1)
            send(ctx, f'И вам выпадают ПРОКЛЯТЫЕ ШТАНЫ ТЕНЕВОГО ЛЕГИОНА! Свет 100 пт, Звук 50 пт, Слепота 75%, +5 Красноречия. А, тут двойное дно. Ну посмотри сам, тогда.')
            return -1 if target.hasPerk(PRK.LUDOMANIA) else 1
        case 567:
            send(ctx, 'Ставки сделаны, ставок больше нет. Что же получит наш герой?')
            target.inv.addSeveralItems(Item.createRandItems(3))
            return -1 if target.hasPerk(PRK.LUDOMANIA) else 1
        case 547:
            send(ctx, 'А ведь они могли в сентябре выпускать шестые свитки!')
            target.inv.addSeveralItems(Item.createRandItemsByType((2, 6), count=1))
            return -1 if target.hasPerk(PRK.LUDOMANIA) else 1
        case 587:
            send(ctx, 'АХАХААХАХАХАХА')
            target.inv.addSeveralItems(Item.createRandItemsByType((3, 4, 8), count=1))
            return -1 if target.hasPerk(PRK.LUDOMANIA) else 1
        case 587:
            send(ctx, 'Ха-ха-ха.')
            target.inv.addSeveralItems(Item.createRandItemsByType((1, 5), count=1))
            return -1 if target.hasPerk(PRK.LUDOMANIA) else 1
        case 347:
            if len(target.inv) == 1:
                send(ctx, 'Нечего копировать.')
                return -1
            send(ctx, str(target.inv))
            send(ctx, 'Укажите номер той одной вещи, которую вы хотите копировать.')
            for event in longpoll.listen():
                if not id_checker(target.id, event): continue
                current = event.obj['message']['text'].lower()
                if current.isdigit() and int(current) <= len(target.inv):
                    stuff = target.inv.getItem(int(current))
                    target.inv.addItem(stuff)
                    target.inv.removeItem(Item(347))
                    send(ctx, f'Предмет {stuff} был успешно скопирован.')
                    break
                else: continue
            return 0
        case 797:
            if invoker.health < invoker.max_hp // 2:
                send(ctx, 'Судья не пойдёт на сделку: ваше поражение будет выглядеть неубедительно.')
                return -1
            send(ctx, f'Судья принимает увесистый мешочек с деньгами, который вы передали ему через подставное лицо. Пересчитав деньги, он делает знак охранникам арены,'
                      f' которые забивают {invoker} и {target} клюшками для гольфа до бессознательного состояния. Вы уходите с позором, зато живые. ')
            invoker.kill()
            target.kill()
            return 1
        case 257:
            target.addEffect(EFF.POISONEDWEAPON, randint(2, 3))
            send(ctx, f'Яд виверны впитывается в ваше оружие.')
            return 1

        # Посохи
        case 558:
            target.acc += 18 + target.lvl
            send(ctx, f'Инструкторский посох добавил вам {18 + target.lvl}% точности.')
            if Chance(target.power + target.lvl):
                return 0
            else:
                send(ctx, f'Вы не проявили должной сноровки при работе с посохом, и он окончательно разрядился.')
                return 1
        case 458:
            send(ctx, f'{target.heal(max(target.dmg, target.power) * 0.6)} ОЗ восстановил Церковный посох.')
            if Chance(target.power + 8 + target.lvl):
                return 0
            else:
                send(ctx, f'Вы не проявили должной сноровки при работе с посохом, и он окончательно разрядился.')
                return 1
        case 448:
            stolen_gold = randint(60, 100 + target.lvl * 15)
            if stolen_gold < target.gold:
                target.gold -= stolen_gold
                target.gold += stolen_gold
                send(ctx, f'{stolen_gold} монет оппонента оседают в вашем кошельке.')
            if stolen_gold >= target.gold > 0:
                target.gold += target.gold
                target.gold = 0
                send(ctx, f'Посох притягивает все монеты, которые были в мошне врага. Мда, небохато - {target.gold} монет.')
            if target.gold == 0:
                send(ctx, 'Денег у врага больше нет( Попробуйте другое действие.')
                return -1
            if Chance(60):
                return 0
            return 1
        case 478:
            target.arm += 12 + target.lvl * 3
            target.resists[SRC.WEAPON].changeValue(target.lvl + 1)
            send(ctx, f'Посох укрепил ваши доспехи на {12 + target.lvl * 3} пунктов и увеличил сопротивление оружию на {target.lvl + 1}%.')
            if Chance(target.power // 2 + 15):
                send(ctx, 'Используя свои познания в магии, вы сумели сохранить еще один заряд в посохе.')
                return 0
            return 1
        case 428:
            send(ctx, f'Никакой мерзкой магии, только проверенные дедовские методы. Вы бьёте палкой {target}, пока не убедитесь, что уроки усвоены.')
            target.levelup(randint(1, 2))
            if Chance(target.dmg + 15): return 0
            return 1
        case 468:
            send(ctx, f'Доспехи были разрушены на {target.destroy_armor(target, 20 + target.lvl, 0)} пт.')
            if Chance(target.power // 2 + 15):
                send(ctx, 'Используя свои познания в магии, вы сумели сохранить еще один заряд в посохе.')
                return 0
            return 1
        case 328:
            if target.createSummon(BeerElemental, ctx):
                send(ctx, 'На зов посоха откликается маниакально-депрессивный Пивной Элементаль.')
            else:
                return -1
            if Chance(target.power // 2 + 10):
                send(ctx, 'Используя свои познания в магии, вы сумели сохранить еще один заряд в посохе.')
                return 0
            return 1

        # Лидерство, военное дело
        case 579:
            for ally in target.getOwnRow():
                ally.ini += ally.ini // 2
            send(ctx, f'Ваша команда чувствует себя гораздо ловчее и быстрее под влиянием штандарта легендарного 47-го полка элитной кавалерии Императора.')
            return 1
        case 999:
            send(ctx, f'Вы поднимаете самое могущественное знамя над своим отрядом.')
            for ally in vb.teams[target.team]:
                if ally.race not in (RACES.UNDEAD, RACES.ARTIFICIAL): ally.morale = 65
                ally.dmg += ally.dmg // 2
                ally.power += ally.power // 2
                ally.acc += 50
            return 1
        case 479:
            for ally in target.getOwnRow():
                ally.dmg = round(ally.dmg * 1.25)
            send(ctx, f'За Императора! За Верховного Канцлера Оттона! Урррраааа!')
            return 1
        case 389:
            for ally in target.getOwnRow():
                ally.health = round(ally.health * 1.4)
            send(ctx, 'Зачарованное знамя придает вам дополнительных жизненных сил в размере 40% от текущего ОЗ.')
            return 1
        case 559:
            for ally in vb.teams[target.team]:
                if ally.race not in (RACES.UNDEAD, RACES.ARTIFICIAL): ally.morale += 15 + target.lvl
            send(ctx, 'Зачарованное знамя придаёт вам дополнительных душевных сил - вы готовы сражаться до конца.')
            return 1
        case 619:
            if not target.isSummon:
                send(ctx, f'Цель не призванное существо.')
                return -1
            target.levelup(target.master.lvl - target.lvl)
            send(ctx, f'Вы дуете в особый рог, который проводит ускоренный курс боевой подготовки для вашего напарника.')
            return 1
        case 329:
            target.addEffect(EFF.BREAKWEAPON, randint(3, 4))
            send(ctx, 'Вы инкрустируете руну в своё оружие. Стильно, модно, молодёжно.')
            return 1
        case 509:
            for ally in target.getOwnRow():
                ally.acc += 30 + target.lvl * 2
            send(ctx, f'Знамя увеличивает вашу точность на {30 + target.lvl * 2}%. Мы очень-очень рады за вас.')
            return 1

        case _:
            send(ctx, f'Предмету с таким кодом ({code}) не были прописаны действия. ')
            return -1


