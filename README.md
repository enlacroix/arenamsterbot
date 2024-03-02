# Sylvenarr: Origins (Master of Arena) - PvP bot for VK
Sylvenarr - текстовая онлайн соревновательная игра в жанре тёмного технофэнтези, вдохновлённая играми Disciples II, Heroes of Might Magic III и Darkest Dungeon. 
Игроки набирают отряд из 4-6 героев, выбирая из двадцати трёх доступных персонажей, обладающих уникальным набором способностей и инвентарём. Смысл игры в том, чтобы победить своего оппонента в пошаговом сражении.

## Персонажи
![](/rsrc/intro2.JPG)

## Запуск
Для запуска вам потребуется сформировать файл ```protected.py``` с данными о боте:
```
TOKEN =
GROUP_ID =
SEND_KEY =
SEND_SERVER =
```

## Ключевые моменты
**Примечание**. *Бот писался достаточно давно, поэтому чистота и качество кода иногда оставляют желать лучшего.*

- работа с базой данных игроков на sqlite3, где сохранялся их прогресс и отмечались рейтинги.
- работа с картинками в PIL: предварительная обработка, добавление объектов, текста, маски. Также бот умел присылать изображения пользователям.
- проектирование системы классов и способностей персонажей. Системы эффектов, вызова существ, инвентаря, торговли и обмена, магии ии заклинаний и т.п.
- возможность сохранения игры и прогресса игроков.
  
**Tech**: ```vk_api, requests, sqlite3, pickle, PIL```

## Система команд
*Читайте руководство для подробной информации!*

Все команды указаны в квадратных скобках, но сами они печатаются без них. Пример: [справка] - дает пояснение по интерфейсу, чтобы её запросить напишите 'справка' в любом регистре. Чтобы вызвать оппонента на дуэль, ответьте на любое его сообщение словом [пвп] (без скобок).   Можно поиграть самим с собой, если просто написать [пвп] в беседу. 
[сдаться] - досрочно завершить сражение.  
[!настройки] - вызвать параметры данного сражения. (см. руководство). 
[!рейтинг] - игра запоминает количество ваших игр и побед, составляя рейтинговую таблицу из всех, кто участвовал в дуэлях.

## Демонстрация

![Вперёд](/rsrc/dm.PNG)

![Как выглядит поле боя](/rsrc/combat.png)

![Славные воины](/rsrc/field.png)


