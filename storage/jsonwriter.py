import json
# reduce(lambda a, x: a + f" {x.cls_name};", vb.archive[winnerTeam], "")
def writeGameInfo(teamlists):
    pass
jsonfile = "statistics.json"

data = {
    "145": [0, 1, 1, 0],
    "347": [0, 1, 0, 0]
}


with open(jsonfile, "w") as write_file:
    json.dump(data, write_file)