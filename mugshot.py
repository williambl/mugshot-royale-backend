from flask import Flask, request, send_from_directory

app = Flask(__name__, static_url_path='')

@app.route("/game/<path:path>")
def send_page(path):
    return send_from_directory("game", path)

@app.route("/upload", methods=["POST"])
def upload():
    print(request.args.get("player"))
    return request.args.get("player")
