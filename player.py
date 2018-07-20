import typing
from json import JSONEncoder

class Player:

    def __init__(self, name: str, addr: str):
        self.name = name
        self.addr = addr
        self.isAlive = True

class PlayerEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Player):
            return {"name": obj.name, "addr": obj.addr, "isAlive": obj.isAlive}
        return json.JSONEncoder.default(self, obj)
