from flask import Flask, request
from flask import render_template
import sqlite3
import os
import time
from apscheduler.schedulers.background import BackgroundScheduler

dbfile = "chess.db"
if "SQLITE_DB" in os.environ:
    dbfile = os.environ["SQLITE_DB"]


db = sqlite3.connect(dbfile)

# Create a player table that will hold their name and thier win loss count for ranking also an elo score 
db.execute('''CREATE TABLE IF NOT EXISTS player
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             playername TEXT UNIQUE,
             wins INTEGER,
             losses INTEGER,
             draws INTEGER)
             ''')

# create a bot table that will hold their name and their win loss count for ranking also an elo score 
db.execute('''CREATE TABLE IF NOT EXISTS bot
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             ownerplayerid INTEGER,
             botname TEXT UNIQUE,
             wins INTEGER,
             losses INTEGER,
             draws INTEGER,
             elo INTEGER)
             ''')

# Create a queue table that holds the current game queue
# The idea is when a player starts a game it will be added to the queue and then when another player joins it will make a match and remove from the queue
db.execute('''CREATE TABLE IF NOT EXISTS queue
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             playerid INTEGER,
             botid INTEGER,
             lastseen INTEGER)
             ''')

# A table that holds the games, History of all fen moves in an array or json and the winner
db.execute('''CREATE TABLE IF NOT EXISTS game
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
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

def mytaskfunc():
    conn = sqlite3.connect(dbfile)
    # delete all players from the queue that have a lastseen more than 20 seconds
    cursor = conn.execute("SELECT * FROM queue WHERE lastseen < ?", (int(round(time.time() * 1000)) - 20000,))
    rows = cursor.fetchall()
    for row in rows:
        conn.execute("DELETE FROM queue WHERE id = ?", (row[0],))
        print(f"deleting game {row[0]} as player did not respond")
    conn.commit()
    conn.close()
    print(f"done cleaning queue") 
    
    

scheduler = BackgroundScheduler()
clean_queue_job = scheduler.add_job(mytaskfunc, 'interval', seconds=10)
scheduler.start()

@app.route("/start-game", methods=["POST"])
def start_game():
    conn = sqlite3.connect(dbfile)
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
    player_id = create_user_and_get_id(conn, player_name)
    bot_id = create_bot_and_get_id(conn, bot_name, player_id)
    if bot_id == -1:
        return "Bot name does not belong to the player please pick a different name or pick a name that you own", 400

    # check if bot is already in the queue
    cursor = conn.execute("SELECT * FROM queue WHERE botid = ?", (bot_id,))
    row = cursor.fetchone()
    if row:
        # extend the timer
        conn.execute("UPDATE queue SET lastseen = ? WHERE id = ?", (int(round(time.time() * 1000)), row[0]))
        conn.commit()
        return "Bot is already in the queue and your timer has been extended to 20 seconds. Send another request by then or you will be removed from the queue", 200
    
    conn.commit()    
    # add bot to the queue
    conn.execute("INSERT INTO queue (id, playerid, botid, lastseen) VALUES (NULL, ?, ?, ?)", (player_id, bot_id, int(round(time.time() * 1000))))
    conn.commit()
    conn.close()
    return f"hi here is your payload {payload} you are player {player_id} and bot {bot_id}", 207


def create_user_and_get_id(conn, player_name):
    # check if the player exists
    cursor = conn.execute("SELECT * FROM player WHERE playername = ?", (player_name,))
    row = cursor.fetchone()
    if not row:
        # create a new player
        conn.execute("INSERT INTO player (playername, wins, losses, draws) VALUES (?, 0, 0, 0)", (player_name,))
        player_id = conn.execute("SELECT id FROM player WHERE playername = ?", (player_name,)).fetchone()[0]
        conn.commit()
    else:
        player_id = row[0]
    return player_id

def create_bot_and_get_id(conn, bot_name, owner_player_id):
    # check if the bot exists
    cursor = conn.execute("SELECT * FROM bot WHERE botname = ?", (bot_name,))
    row = cursor.fetchone()
    if not row:
        # create a new bot
        conn.execute("INSERT INTO bot (ownerplayerid, botname, wins, losses, draws, elo) VALUES (?, ?, 0, 0, 0, 0)", (owner_player_id, bot_name,))
        bot_id = conn.execute("SELECT id FROM bot WHERE botname = ?", (bot_name,)).fetchone()[0]
        conn.commit()
    else:
        # make sure the bot belongs to the proper owner
        if row[1] != owner_player_id:
            return -1
        bot_id = row[0]
    return bot_id

