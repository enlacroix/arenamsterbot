inventory_dict = { # делай пробелы в |
    # 520: ['Аура запрещения | Высасывание маны обоих игроков', 390],
    # 300: ['Аура лепрекона | Ув. удачи на 20 всем лидерам', 290],
    # 410: ['Аура Грогнака | Умен. удачи на 30+ур-нь всем лидерам', 345],
    # 470: ['Аура мужского братства | Обнуление брони лидерам, но у вызывающего броня должна быть >= 45.', 380],
    # 400: ['Аура Размножения | Дублирование предметов в инвентаре обеих лидеров', 310],
    # 330: ['Аура Партнёрства | Восстановление обеим лидерам 50 здоровья, однако вам больше на [уровень*7].', 345],
    # 340: ['Аура аскетизма | Оба лидера теряют 50% золота, но Вам подарок от спонсора', 310],

    411: ['Талисман качалки драугров | Призыв уровневой нежити(с 6 скелет, 12 воин-призрак)', 500],
    431: ['Талисман школы | Призыв шамана гоблинов', 420],
    521: ['Талисман марафона желаний | Призыв Оракула эльфов', 620],
    601: ['Талисман травницы | Призыв Травницы', 580],
    581: ['Талисман брошенных невест | Призыв Полуденницы', 640],
    321: ['Талисман безумного учёного | Призыв Эктоплазмы', 360],
    651: ['Талисман моря | Призыв русалки', 640],
    701: ['Талисман жаркой кузни | Призыв гнома-пиромана', 780],
    541: ['Талисман паскудника | Призыв гоблина-траппера', 380],
    741: ['Талисман перегноя | Призыв Хуорна', 600],
    751: ['Талисман здорового смеха | Призыв Киры (тетрадь со старта =20%)', 660],
    # 781: ['Талисман братвы | Передний ряд занимают 3 гоблина-лучника', 600], # todo

    522: ['Медпакет Древних | +200 ОЗ, снятие отриц эффектов', 400],
    762: ['Механическое сердце | Иммунитет к психическим болезням', 490],
    572: ['Комплект "Сигма" | Призыв Золотого Голема', 490],
    322: ['Бомба с картечью | Неизбежный 40-60 урона по ряду вражеской команды', 400],
    412: ['Пиройлова смола | Огненные чары на оружие ближнего боя', 250],
    562: ['Инъекция | Уменьшает объём лечения цели на 25%', 285],
    662: ['Очки Профессора | Увеличение точности на (40 + ур-нь)%', 685],
    402: ['Нейроусилитель | +50% сопротивление Оглушению, пост.', 420],
    532: ['Мушкет легионера | Стреляй, пока не кончатся патроны', 500],

    343: ['Сфера ужаса | Паралич на 1 ход, Разум', 300],
    353: ['Сфера концентрированного терпения | Наносит урон, зав-щий от вашего стресса, Разум', 360],
    363: ['Сфера проливного Дождя | Снимает все усиления и наносит урон Водой', 370],
    613: ['Сфера ярости | Доп. ход цели', 370],
    323: ['Сфера искажения массы | Враг теряет 30% текущих ОЗ', 355],
    513: ['Сфера женских секретов | Превращает союзника в оракула/русалку/травницу', 400],
    433: ['Сфера гниения плоти | Уменьшает атаку на 30%', 400],
    413: ['Сфера гормонального взрыва | +2 уровня всей команде', 400],
    523: ['Сфера пыток | Превращение союзника в Призрака', 380],
    233: ['Шар клоуна десятилетия | -3 темп развития врагу', 290],


    354: ['Свиток жертвы | Уменьшение резистов к Огню и Смерти на 20+уровень', 365],
    444: ['Свиток Коррозии | Уничтожение случ. пары вещей в инвентаре врага', 370],
    474: ['Свиток незеритовой плоти | +(15+уровень*3) брони, Вард от Оружия', 390],
    454: ['Свиток шейха | -3 уровня врага, забывает случайный перк', 455],
    434: ['Свиток наказания | Ополовинивает максимальное здоровье', 300],
    334: ['Свиток этапирования | Уменьшение резистов к Воздуху и Разуму на 20+уровень', 365],
    404: ['Свиток магического взрыва | урон мана*10, -половина своей маны', 350],


    325: ['Древний фолиант | +3 уровня', 380],
    475: ['Святая вода | Нанесёт 100 урона по саммону-нежити/демону. NERF!', 320],
    465: ['Сандалии Творца | Каждый саммон получает +3 уровня при вызове', 380],
    555: ['Огма Инфиниум | Все навыки использования предметов', 600],
    655: ['Кольцо Понтифика | Воскрешение союзника', 430],
    355: ['Ботинки Апостола | Перк на быстрое перемещение, +20 брони', 375],
    665: ['Фиал самообмана | Ув. макс. здоровья с пересчётом текущего', 515],
    315: ['Индульгенция | Вард и 20% резист к Святому урону', 340],
    715: ['Астральные кандалы | Саммон не исчезнет после смерти хозяина', 555],
    # 712: ['Лампа с ладаном | Даёт всем походившим дополнительный ход', 595],

    346: ['Шлем Пылающего Вереска | Регенерирует ману, 20% резист к Разуму', 350],
    476: ['Кираса Пылающего Вереска | +50 брони и 15% резист к Огню и Смерти', 410],
    516: ['Рукавицы Пылающего Вереска | Увеличивает получаемое лечение на 25%', 405],
    616: ['Сапоги Пылающего Вереска | 75% резист к Смертельному удару', 575],
    216: ['Амулет затмения | Противник теряет 30% силы магии', 350],
    566: ['Тотем возрождения | +1 жизнь', 450],
    276: ['Кукла вуду | Снижение удачи врага на 12+уровень*2 пт', 280],
    406: ['Трансцендентные весы | Обмен значениями маны', 280],
    466: ['Оковы инквизитора | Эффект снижения маны', 350],
    576: ['Клык царя минотавров | Искоренение: -2 жизни цели. Добавит запрет на воскрешение', 460],
    456: ['Кольцо дядюшки Сладкая Доля | +(20 + уровень) Инициативы', 365],
    636: ['Кулон с пером грифона | Эффект контрудара на 3-4 раунда', 405],
    736: ['Латы Титана одиночества | Приравнивает броню к 80, иммунитет к разрушению брони', 600],
    646: ['Чалма султана-ифрита | Эффект Огненного Щита', 375],
    246: ['Кристалл Шантири | Увеличивает силу магии на 14+уровень пт', 290],
    356: ['Амулет рыцаря-раба Гаэнора | +2 к банку критов и уклонений', 300],


    197: ['Кубок костяного придворного | Добавление врагу 20+уровень стресса', 190],
    107: ['Метательный кинжал | Нанести гарант урон, +50% против отравленных', 100],
    207: ['Лунный сахар | Увеличивает на 12+уровень% шанс крита. 2% шанс погибнуть от остановки сердца.', 210],
    407: ['Скуума | Даёт две гарант крит атаки, +10 Инициативы пост. 4% шанс погибнуть от остановки сердца.', 290],
    227: ['Двемерское масло | Увеличение уклонения на 10+уровень', 210],
    287: ['Средство от касадоров | Снимает отравление, даёт вард от Смерти', 280],
    267: ['Настойка опия | Снимает ужас, даёт Вард от Разума', 275],
    117: ['Пиво "Черниговское МЧС" | +(18+уровень) б.духа при стрессе(<0), иначе +12', 130],
    187: ['Отвар алмазной плоти | Пост. увеличение брони на 16+уровень*2 пт', 205],
    237: ['Самоцвет жизни | +75 ОЗ', 140],
    387: ['Баллончик нозафеда | +150 ОЗ', 250],
    2137:['Золотое яблоко | Регенерация ОЗ и бафф брони', 180],
    147: ['Зелье подмастерья | Восстанавливает 3-4 МР ', 150],
    307: ['Эликсир атронаха | Восстанавливает 6-9 МР', 300],
    247: ['Навозный пирог на ниточке | Отравление оппонента', 185],
    257: ['Яд пожилой виверны | Нанести яд на оружие ближнего боя', 300],
    337: ['Парфюм Телванни | Увеличивает торговлю на 25%', 375],
    137: ['Акция компании "Белетор&Сыновья" | На продажу', 320],
    317: ['Отличный мёд Гимли | К атаке прибавляется половина брони, а она всегда обнуляется', 285],
    217: ['Пятизвёздочный коньяк гоблинов | На продажу', 185],
    357: ['Конспекты Принца-Полукровки | +3 темп развития, -1 уровень', 315],
    2187:['Пиво огров "Сливняк" | +(12+уровень*1.5) атаки пост., но накладывает Опьянение', 250],
    397: ['Анисовая водка | Накладывает эффект Силы на 2 раунда', 220],
    347: ['Язык Мимика | Копирование предмета в вашем инвентаре', 290],
    367: ['Эликсир "Слёзы отрицания" | Даёт фиктивные 100 ОЗ, которые исчезнут', 230],
    297: ['Зелье закалки доспеха | Тройной вард от Разрушения брони', 270],
    797: ['Чёрный конверт судьи | Нужно иметь больше половины от макс ОЗ. Убивает вас и выбранного вами врага.', 720],
    # Кейсы.
    167: ['Хитиновый кейс | Случайный предмет 3-4 уровня', 260],
    447: ['Кварцевый кейс | Случайный предмет 5-6 уровня', 420],
    647: ['Милфриловый кейс | Случайный предмет 7-8 уровня', 580],
    747: ['Даэдрический кейс | Случайный ЛЕГЕНДАРНЫЙ предмет', 940],
    547: ['Кейс операции "Звёздное поле" | Случайная Технология или Артефакт любого уровня', 440],
    587: ['Кейс юного мага | Случайная Сфера, Свиток или Посох любого уровня', 420],
    597: ['Кейс операции "Воздушная скала" | Случайный Талисман или Реликвия любого уровня', 450],
    567: ['Кейс операции "Сырная весна" | Три случайные вещи из общего пула предметов игры', 420],

    428: ['Посох пьяного мастера | Увеличение уровня саммона на 2', 390],
    448: ['Посох воришки | Кража золота', 390],
    468: ['Посох ржавчины | Уничтожение брони (не меньше 0)', 380],
    478: ['Посох протектора | +броня и резист к физ урону', 430],
    328: ['Королевский скипетр | Призыв пивного элементаля', 465],
    458: ['Епископский посох св. Ллотиса | Лечение цели', 405],
    558: ['Посох инструктора | Увеличение точности на (18 + уровень)%', 400],

    389: ['Знамя медицинского корпуса | Здоровье ряда х1.4', 410],
    479: ['Знамя рассвета | х1.25 атака ряда', 390],
    559: ['Знамя виктории | +(15+уровень) морали всему отряду', 290],
    509: ['Знамя защитников горна | +точность (30 + уровень*2) на ряд', 450],
    579: ['Штандарт кавалерии | Увел. инициативы на 50% на ряд', 430],
    619: ['Командирский рог | Повышение уровня саммона до своего собственного', 400],
    329: ['Рунный камень ярла | Добавляет к оружию эффект разбития брони', 275],

    # Легендарные
    935: ['Книга пророка Изатиса | 3 дополнительные жизни', 1800],
    932: ['Бластер Чужих | Бесконечный заряд, исключительный урон', 2200],
    906: ['Аркенстон, Завет-Камень Императора | Даёт +50% сопротивлений ко всем источникам', 1700],
    999: ['Красное знамя | Максимальный боевой дух, +50% точности и атаки', 2200],
}

def check_inventory(template_inventory_dict):
    for key, value in template_inventory_dict.items():
        if len(value[0].split(' | ')) != 2:
            print(f'Ошибка в описании предмета {key}:{value}!')

# print('Имя | Редкость | Тип')
# n = 1
# for elem in inventory_dict.keys():
#     print(n, inventory_dict[elem][0].split("|")[0], '|', str(elem)[0], '|', categories_of_items[int(str(elem)[-1])])
#     n += 1
# uwu = {'Ауры': 0, 'Талисманы': 0, 'Технологии': 0, 'Сферы': 0, 'Свитки': 0, 'Реликвии': 0, 'Артефакты': 0, 'Расходники': 0, 'Посохи': 0, 'Лидерство': 0}
# for elem in inventory_dict.keys():
#     uwu[categories_of_items[elem % 10]] += 1
# print(uwu)
# gifs_of_heroes_dict = {1: 'http://nevendaar.com/_ph/35/2/765703425.gif', 4: 'http://nevendaar.com/_ph/40/2/831770939.gif'}