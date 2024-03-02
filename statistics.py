import pickle

from utils import mergeTwoDicts
from background import stats_dict




NUM_CHARS = {'Assassin': 1, 'Paladin': 2, 'Inquisitor': 3, 'Detective': 4, 'DemonLord': 5, 'Abbess': 6, 'OrcKing': 7, 'Marauder': 8, 'Archlich': 9, 'Witch': 10,
             'GhostWarrior': 11, 'Specter': 12, 'Oracle': 13, 'Herbalist': 14, 'Demiurge': 15, 'GoldGolem': 16, 'BeerElemental': 17, 'Knight': 18, 'Mermaid': 19, 'Patriarch': 20,
             'Pyro': 21, 'EvilTree': 22, 'Dracolich': 23}
'''
ile "C:\PycharmProjects\OLDVKSYLVENAR\statistics.py", line 20, in processTeamList
    values[i][NUM_CHARS[unit.__class__.__name__] - 1] = 1
              ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'GoblinShaman'
если архивируешь с загрузки, то будет шаман 
'''

def processTeamList(teamArray: list[list, list]) -> dict[int, list] | None:
    keys = [teamArray[0][0].id, teamArray[1][0].id]
    if keys[0] == keys[1]: return None
    values = [[0]*len(NUM_CHARS), [0]*len(NUM_CHARS)]
    for i, tlist in enumerate(teamArray):
        for unit in tlist:
            values[i][NUM_CHARS[unit.__class__.__name__] - 1] = 1
    return dict(zip(keys, values))




def loadStatistics():
    with open("storage\\statistics.json", "rb") as f:
        return pickle.load(f)

def saveCharsCombinations(newInfo: dict[int, list]):
    load = loadStatistics()
    with open("storage\\statistics.json", "wb") as f:
        pickle.dump(mergeTwoDicts(load, newInfo), f, 0)


newData = {349167814: [-1, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0], 374126844: [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]}


def showStatistics(vk_id):
    load: dict = loadStatistics()
    info = load.get(vk_id, None)
    report = 'Было сыграно партий за: \n'
    if info is None: return False
    for i, elem in enumerate(info):
        clsName = list(NUM_CHARS.keys())[list(NUM_CHARS.values()).index(i+1)]
        report += f'{stats_dict[clsName].nm}: {elem} '
        if (i + 1) % 4 == 0: report += '\n'
    return report

