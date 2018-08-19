from flask import Flask, request, send_from_directory, make_response, redirect
import json
from flask_socketio import SocketIO, emit
from player import *
import os
import asyncio
from haversine import haversine
from game import *

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = "secret_key"
socketio = SocketIO(app, engineio_logger=True)
players = []
config = {}
game = None

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return send_from_directory("game", "login.html")
    elif request.method == "POST":
        if (not config["unique_names_allowed"] and is_unique_name(request.form["name"])):
            return redirect("login")
        new_id = request.form["name"] + str(len(players))
        new_player = Player(request.form["name"], request.remote_addr, request.form["name"] in config["admins"], "", new_id)
        players.append(new_player)
        socketio.emit("player-joined", {"name": request.form["name"]}, namespace="/websocket", broadcast=True)
        response = redirect("/")
        response.set_cookie("id", new_id)
        return response

@app.route("/")
def send_root():
    if not is_valid_id(request.cookies.get("id")):
        return redirect("login")
    return redirect("/game/index.html")

@app.route("/game/<path:path>")
def send_page(path):
    if not is_valid_id(request.cookies.get("id")):
        return "403 Unauthorised", 403
    return send_from_directory("game", path)

@app.route("/upload", methods=["POST"])
def upload():
    if not is_valid_id(request.cookies.get("id")):
        return "403 Unauthorised", 403
    print(request.args.get("player"))
    with open(request.args.get("player")+".jpg", "wb") as f:
        f.write(request.data)

    for player in players:
        if player.name == request.args.get("player"):
            player.isAlive = False
            socketio.emit("player-eliminated", {"name": player.name, "id": player.id}, namespace="/websocket", broadcast=True)

    return request.args.get("player")

@app.route("/players")
def send_player_list():
    return json.dumps(players, cls=PlayerEncoder)

@socketio.on('connect', namespace='/websocket')
def websocket_connect():
    print("connected!")

@socketio.on('disconnect', namespace='/websocket')
def websocket_disconnect():
    name = ""
    for player in players:
        if player.addr == request.remote_addr:
            name = player.name
            players.remove(player)
    print(name + ' disconnected')
    emit("player-left", {"name": name}, broadcast=True)

@socketio.on("start-game-request", namespace="/websocket")
def handle_start_game_request(data):
    print("received start-game-request")
    admin = None
    for player in players:
        if player.addr == request.remote_addr and player.isAdmin:
            admin = player
    print(admin.name + "has started the game!");
    print(json)
    emit("start-game", {"rad": data["rad"], "lat": data["lat"], "long": data["long"], "time": data["time"]}, broadcast=True)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(start_game(float(data["lat"]), float(data["long"]), float(data["rad"]), float(data["time"])))

@socketio.on("position", namespace="/websocket")
def check_position(data):
    print("Received position!")
    if haversine((data["lat"], data["long"]), (game.lat, game.long)) > game.rad:
        for player in players:
            if player.addr == request.remote_addr:
                player.hp -= 1;
                print(player.name + " is outside the safe zone! Their hp is now " + player.hp)

def parse_config():
    try:
        with open(os.path.join(os.path.expanduser("~/.config/mugshot-royale"),"config.json"), 'r') as config_file:
            global config
            config = json.loads(config_file.read())
    except IOError:
        try:
            os.makedirs(os.path.expanduser("~/.config/mugshot-royale"))
        except IOError:
            pass
        open(os.path.join(os.path.expanduser("~/.config/mugshot-royale"),"config.json"), 'a').close()

def is_valid_id(id_to_check):
    for player in players:
        if (player.id == id_to_check):
            return True
    return False

def is_unique_name(name_to_check):
    for player in players:
        if (player.name == name_to_check):
            return False
    return True


async def start_game(lat, long, rad, freq):
    global game
    game = Game(lat, long, rad, freq, socketio)
    await check_player_positions(10)
    for i in range(1, 5):
        await game.shrink_safe_zone()

async def check_player_positions(freq):
    while True:
        await asyncio.sleep(freq)
        print("checking!")
        socketio.emit("send-position", namespace="/websocket", broadcast=True)

if __name__ == "__main__":
    parse_config()
    socketio.run(app, host="0.0.0.0")
