from flask import Flask, request, send_from_directory, make_response, redirect
from player import Player

app = Flask(__name__, static_url_path='')
players = []

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return send_from_directory("game", "login.html")
    elif request.method == "POST":
        players.append(Player(request.form.get("name"), request.remote_addr))
        response = redirect("/")
        response.set_cookie("id", str(len(players)-1))
        return response

@app.route("/")
def send_root():
    if request.cookies.get("id") == None:
        return redirect("login")
    return redirect("/game/index.html")

@app.route("/game/<path:path>")
def send_page(path):
    return send_from_directory("game", path)

@app.route("/upload", methods=["POST"])
def upload():
    print(request.args.get("player"))
    with open(request.args.get("player")+".jpg", "wb") as f:
        f.write(request.data)
    return request.args.get("player")
