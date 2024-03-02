import pickle

PIK = "mysave.txt"

def saveGame(teamList: list[list[list, list], list, list, int]):
    with open(PIK, "wb") as f:
        pickle.dump(teamList, f)

def loadGame() -> list[list[list, list], list, list, int]:
    with open(PIK, "rb") as f:
        return pickle.load(f)


