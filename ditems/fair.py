from functools import reduce
from random import randint, sample
from background import stats_dict
from datastore.dperks import ITEMPERKS
from ditems.itemcls import Item
from settings import SHOP_SIZE
from vkmodule import send, longpoll, id_checker
import varbank as vb


def enoughMoney(unit, item):
    if item.getPurchasePrice(unit) <= vb.Team.Entry(unit.team).gold: return '💰'
    return ''

def show_prices(unit, shopList):
    if len(shopList) == 0: return 'Всё распродано.'
    output = ''
    for i, item in enumerate(shopList):
        output += f'{i+1}. {item.name} ({item.getPurchasePrice(unit)} зол), {item.showAbility(unit)} {enoughMoney(unit, item)}\n{item.description}. \n'
    return f'{unit}, [{unit.team + 1}]: \n {output} \n [куп n] - Купить товар с номером n. \n [инв] - Увидеть свой инвентарь с расценками. \n' \
    '[прод n] - Продать товар с номером n. \n [стоп] - Завершить покупки.'


def individual_trade(unit, shopList: list[Item], beginEvent):
    """
    Инвестирование золота в магазин: на следующую ярмарку большая скидка и лучше ассортимент.
    Реализация разных скидок для игроков.
    """
    send(beginEvent, show_prices(unit, shopList))
    send(beginEvent, f'Баланс вашей команды: {vb.Team.Entry(unit.team).gold} монет. Навык торговли: {round(unit.merchant * 100)}%. \n Перки команды: {", " .join([perk.value[0] for perk in set(reduce(lambda a, x: a + x.skills, vb.teams[unit.team], [])) if perk in ITEMPERKS])}')
    for event in longpoll.listen():
        if not id_checker(unit.id, event): continue
        try:
            current = event.obj['message']['text'].lower()
        except:
            continue
        match current.split(' '):
            case ['куп', n] if n.isdigit() and 1 <= int(n) <= len(shopList):
                good: Item
                good = shopList[int(n) - 1]
                if good.getPurchasePrice(unit) > vb.Team.Entry(unit.team).gold:
                    send(event, f'Вам не хватает {good.getPurchasePrice(unit) - vb.Team.Entry(unit.team).gold} золота для приобретения {good}.')
                    continue
                else:
                    vb.Team.Entry(unit.team).gold -= good.getPurchasePrice(unit)
                    unit.inv.addItem(good) # TODO решить кому из команды отдать предмет.
                    shopList.remove(good)
                    send(event, f'Благодарим за приобретение {good}!')
                    break
            case ['инв' | 'i' | 'ш']:
                send(event, unit.inv.showInventoryWithPrices())  # Защита от спекулянтов. 0.925 = СРЕД(0.7, 1.15)
                continue
            case ['прод', n] if n.isdigit() and 1 <= int(n) <= len(unit.inv):
                sell: Item
                sell = unit.inv.getItem(int(n))
                assert sell is not None, 'ЧЗХ'
                vb.Team.Entry(unit.team).gold += sell.getSalePrice(unit)
                unit.inv.removeItem(sell)
                shopList.append(sell)
                send(event, f'Вот ваши деньги. Мы найдем достойное применение {sell}.')
                break
            case ['прод', 'все' | 'всё']:
                for item, amount in list(unit.inv.pool.items()): # учитывай количество при продаже
                    vb.Team.Entry(unit.team).gold += item.getSalePrice(unit) * amount
                    unit.inv.removeItem(item, amount)
                    shopList.append(item)
                send(event, f'Вы продаёте все предметы из инвентаря. Поздравляем.')
                break
            case ['стоп']:
                send(event, 'Досвиданияспасибоприходитеещё.')
                vb.Team.Entry(unit.team).gold += round(stats_dict[unit.__class__.__name__].gold * 1.35 + randint(50, 100))
                return False
            case _:
                continue


def competitive_trade(A, B, ctx):
    """

    l = sorted([A, B], key=lambda x: x.ini + x.gold/75, reverse=True)
    Конкурентные торги. Генерируется один список на всех из 12 объектов. Игрок А покупает из него одну вещь на выбор, потом ход переходит к игроку В,
    до тех пока ОБА не напишут стоп. Если один напишет стоп, то второй игрок покупает до того, пока сам не прекратит.
    :param A: l[0] тот у которого большая инициатива / начинающим первым
    :param B: l[1] догоняющий
    """
    shop = Item.createRandItems(SHOP_SIZE)
    flag_a, flag_b = None, None
    while True:
        if flag_a is None:
            flag_a = individual_trade(A, shop, ctx)
        if flag_b is None:
            flag_b = individual_trade(B, shop, ctx)
        if flag_a is not None and flag_b is not None:
            send(ctx, 'Ярмарка завершена, а теперь мы вернемся к этому увлекательному противостоянию.')
            break