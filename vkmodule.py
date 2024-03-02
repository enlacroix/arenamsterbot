import requests
import vk_api
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll
from protected import TOKEN, GROUP_ID, SEND_KEY, SEND_SERVER

vk_session = vk_api.VkApi(token=TOKEN)
longpoll = VkBotLongPoll(vk_session, GROUP_ID)
vk = vk_session.get_api()


def ls_send(event, report):
    vk.messages.send(
        user_id=int(event.obj.message['from_id']),
        message=report,
        random_id=get_random_id()
    )


def send(event, report):
    if event.from_chat:
        vk.messages.send(
            key=SEND_KEY,
            server=SEND_SERVER,
            ts='1',
            random_id=get_random_id(),
            message=report,
            chat_id=event.chat_id
        )


# import VkBotEventType - для отслеживания if Message.NEW - пришло ли это сообщение от бота.

def get_first_name(_id):
    """
    :param _id: айди
    :return: имя пользователя
    last_name = user_get['last_name'] - как получить фамилию.
    """
    user_get = vk.users.get(user_ids=_id)
    try:
        user_get = user_get[0]
        first_name = user_get['first_name']
    except IndexError:
        first_name = 'Бот'
    return first_name


def id_checker(id0, event):
    id_x = int(event.obj.message['from_id'])
    if id_x == id0:
        return 1
    else:
        print(f'Жулик {get_first_name(id_x)}, сейчас ход игрока {get_first_name(id0)}!')
        return 0


def send_photo(description, event, path):
    a = vk_session.method("photos.getMessagesUploadServer")
    b = requests.post(a['upload_url'],
                      files={'photo': open(f'{path}', 'rb')}).json()
    c = vk_session.method('photos.saveMessagesPhoto', {'photo': b['photo'], 'server': b['server'], 'hash': b['hash']})[
        0]
    d = "photo{}_{}".format(c["owner_id"], c["id"])
    vk_session.method("messages.send",
                      {"chat_id": event.chat_id, "message": str(description), "attachment": d, "random_id": 0})


def sendSeveralPhoto(description, event, listOfPaths):
    a = vk_session.method("photos.getMessagesUploadServer")
    res = []
    for path in listOfPaths:
        b = requests.post(a['upload_url'], files={'photo': open(f'{path}', 'rb')}).json()
        c = vk_session.method('photos.saveMessagesPhoto', {'photo': b['photo'], 'server': b['server'], 'hash': b['hash']})[
            0]
        d = f'photo{c["owner_id"]}_{c["id"]}'
        res.append(d)
    res = ','.join(res)
    vk_session.method("messages.send", {"chat_id": event.chat_id, "message": str(description), "attachment": res, "random_id": 0})