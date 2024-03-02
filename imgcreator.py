"""
Модуль, отвечающий за создание картинки, которая выводится в конце каждого раунда.
1. В начале функции combat создается сочетание base + randint(1, 12).png, которая задает задний фон всего сражения.
2. Конец раунда.
- Мы запрашиваем классы всех присутствующих персонажей по командам и размещаем портреты согласно словарю "класс-название".
- Узнаем текущие характеристики и размещаем их в нужном месте.
- Размещаем фигурки на поле боя. Для команды 0 ставим как обычно, а для команды 1 фигурки надо бы отзеркалить.
- Сохраняем получившуюся картинку result.png в директории imgs и заставляем бота отправить её в беседу.
- Произойдет автоудаление и весь процесс начнется заново.
3. Удалить картинку combat.png
"""
from PIL import Image, ImageFont, ImageDraw
from random import randint

'''
from characters.bandit import Bandit
from characters.ordinator import Ordinator
from summon_classes.misc import Specter
from summon_classes.misc import Gargoyle
A = Bandit(1456)
B = Ordinator(4571)
A.team = 0
B.team = 1
C = Specter(A)
D = Gargoyle(A)

teams = [[A, C], [B]]
stats1 = [1, 100, 20, 25, 50, 42, 12, 20, 15, 20]
'''

'''
font = ImageFont.truetype('C:\WINDOWS\Fonts\Century.ttf', size=20)
    draw_text = ImageDraw.Draw(mask_im)
    draw_text.text((310, 150), f'{str(A)} vs {str(B)}', font=font, fill='black')
'''
font = ImageFont.truetype('C:\WINDOWS\Fonts\Century.ttf', size=12)

def create_start_image(A, B):
    im0 = Image.open('imgs\\backgrounds\\base_0.png')
    im1 = Image.open(f'imgs\\backgrounds\\{randint(1, 20)}.png').convert("RGBA")
    mask_im = Image.new("RGBA", im0.size, 0)
    mask_im.paste(im0, (0, 0))
    mask_im.paste(im1, (0, 0), mask=im1)
    try:
        im2 = Image.open(f'imgs\\characters\\{A.__class__.__name__}.png').convert("RGBA")
        im3 = Image.open(f'imgs\\characters\\{B.__class__.__name__}.png').convert("RGBA")
    except FileNotFoundError:
        im2 = Image.open(f'imgs\\characters\\Imp.png').convert("RGBA")
        im3 = Image.open(f'imgs\\characters\\Imp.png').convert("RGBA")
    # im4 = Image.open(f'imgs\\figures\\{A.__class__.__name__}.png').convert("RGBA")
    # im5 = Image.open(f'imgs\\figures\\{B.__class__.__name__}.png').convert("RGBA")
    mask_im.paste(im2, (-45, 75), mask=im2)
    mask_im.paste(im3, (690, 75), mask=im3)
    # mask_im.paste(im4, (300, 200), mask=im4)
    # mask_im.paste(im5, (580, 200), mask=im5)
    mask_im.save('imgs\\combat.png', quality=95)


def makeFieldImage(teamList):
    im0 = Image.open('imgs\\backgrounds\\scbase.png')
    im1 = Image.open(f'imgs\\backgrounds\\scroll.png').convert("RGBA")
    #mask_im = Image.new("RGBA", im1.size, 0)
    mask_im = Image.new("RGBA", im0.size, 0)
    mask_im.paste(im0, (0, 0))

    mask_im.paste(im1, (0, 0), mask=im1)
    draw_text = ImageDraw.Draw(mask_im)

    for i, team in enumerate(teamList):
        for j, unit in enumerate(team):
            try:
                im2 = Image.open(f'imgs\\portraits\\{unit.__class__.__name__}.png').convert("RGBA")
            except FileNotFoundError:
                im2 = Image.open(f'imgs\\portraits\\DEFAULT.PNG').convert("RGBA")
            X = 290 + 200**i + unit.position * 100 * (-1)**(i+1)
            Y = 110 + unit.column*110
            draw_text.text((X, Y-18), f'{j+1}. HP {unit.health}, {unit.lvl} lvl', font=font, fill='black')
            mask_im.paste(im2, (X, Y), mask=im2)
    mask_im.save('imgs\\field.png', quality=95)


# class Assassin:
#     def __init__(self, position=0, column=0):
#         self.position = position
#         self.column = column
#         self.health = 50
#         self.maxhp = 100
#         self.level = 1
#
#
# class Demiurge:
#     def __init__(self, position=0, column=0):
#         self.position = position
#         self.column = column
#         self.health = 99
#         self.maxhp = 200
#         self.level = 9
#
#
# class OrcKing:
#     def __init__(self, position=0, column=0):
#         self.position = position
#         self.column = column
#         self.health = 9
#         self.maxhp = 200
#         self.level = 15
#
#
# class Patriarch:
#     def __init__(self, position=0, column=0):
#         self.position = position
#         self.column = column
#         self.health = 9
#         self.maxhp = 50
#         self.level = 1
#
# # todo добавлять номера героев в соотв с порядком. указать хп и уровень
# makeFieldImage([[Assassin(0, 0), Assassin(0, 1), Demiurge(1, 0), OrcKing(1, 1), Patriarch(1, 2)], [OrcKing(0, 0), Patriarch(0, 1), Assassin(1, 1)]])
# def create_summon_image(X, Y):
#     '''
#     :param X: A.summon
#     :param Y: B.summon
#     '''
#     if X is None and Y is None:
#         return 0
#     im0 = Image.open(f'imgs\\summons\\back{randint(1, 5)}.png')
#     mask_im = Image.new("RGBA", im0.size, 0)
#     mask_im.paste(im0, (0, 0))
#     if X is not None:
#         im1 = Image.open(f'imgs\\summons\\{X.cls_name}.png').convert("RGBA")
#         mask_im.paste(im1, (-20, 100), mask=im1)
#     if Y is not None:
#         im2 = Image.open(f'imgs\\summons\\{Y.cls_name}.png').convert("RGBA")
#         mask_im.paste(im2, (450, 100), mask=im2)
#     mask_im.save('imgs\\round.png', quality=95)
