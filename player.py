import typing
from json import JSONEncoder

class Player:

    def __init__(self, name: str, addr: str, isAdmin: bool, team: str, id: str):
        self.name = name
        self.addr = addr
        self.isAlive = True
        self.isAdmin = isAdmin
        self.team = team
        self.hp = 6
        self.id = id

class PlayerEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Player):
            return {"name": obj.name, "addr": obj.addr, "isAlive": obj.isAlive, "isAdmin": obj.isAdmin, "team": obj.team, "id": obj.id}
        return json.JSONEncoder.default(self, obj)
