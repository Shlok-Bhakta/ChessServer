from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    f = open("chess.html", "r")
    content = f.read()
    f.close()
    return content

@app.route("/clicked", methods=["POST"])
def clicked():
    return "<h1>Clicked!</h1>"