"""
Основная программа, в которой запускатеся бот. Здесь происходит идентификация команды от пользователя и инструкции какие функции вызывать.
Команда см статы, которая выводит инфу по себе или по противнику.
Можно ли красиво оформлять текст в ВК? ascii таблицами?
"""
import traceback
from random import randint
import pvp
from storage.database import get_sql_rating
from storage.savegame import saveGame
from settings import show_settings
from statistics import showStatistics
from vkmodule import longpoll, send, get_first_name
import varbank as vb

for event in longpoll.listen():
    if '!настройки' in str(event).lower():
        send(event, show_settings())

    if 'пвп' in str(event).lower() or 'gdg' in str(event).lower(): #event.obj['message']['text'].lower().startswith('пвп')
        id1 = event.obj.message["from_id"]
        try:
            id2 = event.obj.message['reply_message']['from_id']
        except KeyError:
            # pass
            send(event, 'Оппонент для пвп не был выбран, была запущена игра против себя.')
            id2 = id1
        try:
            pvp.combat(event, id1, id2)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            saveGame([vb.teams, vb.done, vb.delayed, vb.stage])
            send(event, 'Аварийное завершение игры. Без паники! Наши лучшие программисты уже работают над исправлением ошибок. Игру можно продолжить по команде [загрузить].')
            break

    if 'загрузить' in str(event).lower() or 'лоад' in str(event).lower():
        pvp.combat(event, 0, 0, loadFlag=True)

    if '!яндекс' in str(event):
        send(event, f'[id{str(event.obj.message["from_id"])}|{get_first_name(event.obj.message["from_id"])}], вы на {str(randint(0, 100))}% преданны Яндексу. ')


    if '!рейтинг' in str(event):
        send(event, get_sql_rating())

    if '!обзор' in str(event):
        id_ = event.obj.message["from_id"]
        send(event, f'[id{str(id_)}|{get_first_name(id_)}], ваша статистика: \n {showStatistics(id_)}')

    '''
    Команда запоминания сообщений из первой версии. Предложения:
    - записывать в бд, но не только текст, но и: автора и время. 
    - цитаты можно смотреть и просматривать случайные / либо топ из них, либо самые старые и т.д.
    '''
    # if '!закреп' in str(event):
    #     message_report = event.obj['message']
    #     text1 = message_report['text'][8:]
    #     f1 = open('auf.txt', 'a')
    #     f1.write(text1 + '\n')
    #     f1.close()
    #     pin_report = 'Сообщение ' + '"' + text1 + '"' + ' успешно добавлено в цитатник. Любо!'
    #     send_message(pin_report)

