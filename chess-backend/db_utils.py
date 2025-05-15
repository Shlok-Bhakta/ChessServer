import sqlite3
import os
import time
import random
# chess module is not directly used by functions in this file,
# but was in the original app.py imports.
# If any future db util needs it, it's here. Otherwise, it can be removed.
import chess

dbfile = "chess.db"
if "SQLITE_DB" in os.environ:
    dbfile = os.environ["SQLITE_DB"]

def get_db_connection():
    conn = sqlite3.connect(dbfile)
    conn.row_factory = sqlite3.Row  # Enable access by column name
    return conn

def init_db():
    conn = get_db_connection()
    # Create a player table that will hold their name and thier win loss count for ranking also an elo score 
    conn.execute('''CREATE TABLE IF NOT EXISTS player
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 playername TEXT UNIQUE,
                 wins INTEGER,
                 losses INTEGER,
                 draws INTEGER)
                 ''')
    
    # create a bot table that will hold their name and their win loss count for ranking also an elo score 
    conn.execute('''CREATE TABLE IF NOT EXISTS bot
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
    conn.execute('''CREATE TABLE IF NOT EXISTS queue
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 playerid INTEGER,
                 botid INTEGER,
                 lastseen INTEGER)
                 ''')
    
    # A table that holds the games, History of all fen moves in an array or json and the winner
    conn.execute('''CREATE TABLE IF NOT EXISTS game
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 isactive INTEGER,
                 whiteplayerid INTEGER,
                 blackplayerid INTEGER,
                 whitebotid INTEGER,
                 blackbotid INTEGER,
                 winnerplayerid INTEGER,
                 winnerbotid INTEGER,
                 moves TEXT,
                 whiteplayereval TEXT,
                 blackplayereval TEXT,
                 stockfisheval TEXT,
                 timesettings TEXT,
                 blackplayertime INTEGER,
                 whiteplayertime INTEGER,
                 requestsent INTEGER,
                 starttime INTEGER,
                 endtime INTEGER)
                 ''')
    conn.commit()
    conn.close()

def init_game(conn, player_id, opponent_player_id, bot_id, opponent_bot_id):
    timesettings = "2+0"
    timecontrol = timesettings.split("+")
    totaltime = int(timecontrol[0]) * 60
    increment = int(timecontrol[1])

    # next create a game entry
    # flip a coin for who is black
    if random.randint(0, 1) == 0:
        conn.execute("""INSERT INTO game 
        (isactive, whiteplayerid, blackplayerid, whitebotid, blackbotid, winnerplayerid, winnerbotid, moves, whiteplayereval, blackplayereval, stockfisheval, timesettings, blackplayertime, whiteplayertime, requestsent, starttime, endtime) 
        VALUES (1, ?, ?, ?, ?, NULL, NULL, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", "0.0", "0.0", "0.0", ?, ?, ?, NULL, ?, NULL)""", 
        (opponent_player_id, player_id, opponent_bot_id, bot_id, timesettings, totaltime, totaltime, int(round(time.time() * 1000))))
    else:
        conn.execute("""INSERT INTO game 
        (isactive, whiteplayerid, blackplayerid, whitebotid, blackbotid, winnerplayerid, winnerbotid, moves, whiteplayereval, blackplayereval, stockfisheval, timesettings, blackplayertime, whiteplayertime, requestsent, starttime, endtime) 
    VALUES (1, ?, ?, ?, ?, NULL, NULL, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", "0.0", "0.0", "0.0", ?, ?, ?, NULL, ?, NULL)""",        
        (player_id, opponent_player_id, bot_id, opponent_bot_id, timesettings, totaltime, totaltime, int(round(time.time() * 1000))))

    conn.commit()

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


def get_user_id_from_name(conn, player_name):
    cursor = conn.execute("SELECT * FROM player WHERE playername = ?", (player_name,))
    row = cursor.fetchone()
    if not row:
        return -1
    return row[0]

def get_bot_id_from_name(conn, bot_name):
    cursor = conn.execute("SELECT * FROM bot WHERE botname = ?", (bot_name,))
    row = cursor.fetchone()
    if not row:
        return -1
    return row[0]

def check_bot_ownership(conn, bot_id, player_id):
    cursor = conn.execute("SELECT * FROM bot WHERE id = ?", (bot_id,))
    row = cursor.fetchone()
    if not row:
        return -2
    if row[1] != player_id:
        return -1
    return 0