import typing

class Player:

    def __init__(self, name: str, addr: str):
        self.name = name
        self.addr = addr
        self.isAlive = True
