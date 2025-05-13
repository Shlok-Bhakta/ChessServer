from flask import Flask, request
from flask import render_template
import sqlite3
import os

dbfile = "chess.db"
if "SQLITE_DB" in os.environ:
    dbfile = os.environ["SQLITE_DB"]


db = sqlite3.connect(dbfile)

# Create a player table that will hold their name and thier win loss count for ranking also an elo score 
db.execute('''CREATE TABLE IF NOT EXISTS player
             (id INTEGER PRIMARY KEY, 
             name TEXT,
             wins INTEGER,
             losses INTEGER,
             draws INTEGER,
             elo INTEGER)
             ''')

# Create a queue table that holds the current game queue
# The idea is when a player starts a game it will be added to the queue and then when another player joins it will make a match and remove from the queue
db.execute('''CREATE TABLE IF NOT EXISTS queue
             (id INTEGER PRIMARY KEY, 
             playerid INTEGER,
             botname TEXT,
             lastseen INTEGER)
             ''')
# clear the queue
db.execute('''DELETE FROM queue''')

# A table that holds the games, History of all fen moves in an array or json and the winner
db.execute('''CREATE TABLE IF NOT EXISTS games
             (id INTEGER PRIMARY KEY, 
             isactive INTEGER,
             whiteplayerid INTEGER,
             blackplayerid INTEGER,
             winnerplayerid INTEGER,
             moves TEXT,
             whiteplayereval TEXT,
             blackplayereval TEXT,
             stockfisheval TEXT,
             timesettings TEXT,
             blackplayertime INTEGER,
             whiteplayertime INTEGER,
             starttime INTEGER,
             endtime INTEGER)
             ''')

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


@app.route("/start-game", methods=["POST"])
def start_game():
    # expected format {'player_name': 'shlok', 'bot_name': 'LazySuzan'}
    payload = request.get_json()
    # validate the payload
    if not payload:
        return "No payload", 400
    if not payload.get("player_name") and not payload.get("bot_name"):
        return "No player_name or bot_name", 400
    if not payload.get("player_name"):
        return "No player_name", 400
    if not payload.get("bot_name"):
        return "No bot_name", 400

    player_name = payload.get("player_name")
    bot_name = payload.get("bot_name")

    # check if bot is already in the queue
    cursor = db.execute("SELECT * FROM queue WHERE botname = ?", (bot_name,))
    row = cursor.fetchone()
    if row:
        return "Bot is already in the queue", 400
    



    return f"hi here is your payload {payload}", 207