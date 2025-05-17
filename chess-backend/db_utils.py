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
        VALUES (1, ?, ?, ?, ?, NULL, NULL, "", "0.0", "0.0", "0.0", ?, ?, ?, NULL, ?, NULL)""", 
        (opponent_player_id, player_id, opponent_bot_id, bot_id, timesettings, totaltime, totaltime, int(round(time.time() * 1000))))
    else:
        conn.execute("""INSERT INTO game 
        (isactive, whiteplayerid, blackplayerid, whitebotid, blackbotid, winnerplayerid, winnerbotid, moves, whiteplayereval, blackplayereval, stockfisheval, timesettings, blackplayertime, whiteplayertime, requestsent, starttime, endtime) 
    VALUES (1, ?, ?, ?, ?, NULL, NULL, "", "0.0", "0.0", "0.0", ?, ?, ?, NULL, ?, NULL)""",        
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

def check_game(board: chess.Board, time_left):
    if board.is_checkmate():
        return 1
    if board.is_stalemate():
        return -1
    if board.is_insufficient_material():
        return -1
    if board.is_fivefold_repetition():
        return -1
    if board.is_fifty_moves():
        return -1
    if time_left <= 0:
        return 1
    return 0


def reconstruct_board(moves):
    moves_list = []
    if moves != "":
        moves_list = moves.split(",")
    col = 0
    board = chess.Board(chess.STARTING_FEN)
    for move in moves_list:
        chess_move = chess.Move.from_uci(move)
        if col % 2 == 0:
            board.turn = chess.WHITE
        else:
            board.turn = chess.BLACK
        board.push(chess_move)
        col += 1
    return board

def add_move(board, move_val, color):
    if color == "white":
        board.turn = chess.WHITE
    else:
        board.turn = chess.BLACK
    # TODO proper validation of the move
    move = chess.Move.from_uci(move_val)
    board.push(move)
    return board

def handle_potential_game_over(conn, board, id, time, player_id, bot_id):
    game_over = check_game(board, time)
    if game_over == 1: # win
        conn.execute("UPDATE game SET isactive = ? WHERE id = ?", (-1, id))
        conn.execute("UPDATE game SET winnerplayerid = ? WHERE id = ?", (player_id, id))
        conn.execute("UPDATE game SET winnerbotid = ? WHERE id = ?", (bot_id, id))
        conn.commit()
        conn.close()
        return "you win", 202
    elif game_over == -1: # draw
        conn.execute("UPDATE game SET isactive = ? WHERE id = ?", (-1, id))
        conn.execute("UPDATE game SET winnerplayerid = NULL WHERE id = ?", (id))
        conn.execute("UPDATE game SET winnerbotid = NULL WHERE id = ?", (id))
        conn.commit()
        conn.close()
        return "draw", 202
    return None

def update_time_and_moves_and_isactive(conn, id, time, moves_list, move, color):
    move_string = ""
    if(moves_list == ""):
        moves_list = move
        move_string = move
    else:
        moves_list = moves_list.split(",")
        moves_list.append(move)
        move_string = ','.join(moves_list)
    conn.execute("UPDATE game SET moves = ? WHERE id = ?", (move_string, id))
    if color == "white":
        conn.execute("UPDATE game SET whiteplayertime = ? WHERE id = ?", (time, id))
        conn.execute("UPDATE game SET isactive = ? WHERE id = ?", (2, id))
    else:
        conn.execute("UPDATE game SET blackplayertime = ? WHERE id = ?", (time, id))
        conn.execute("UPDATE game SET isactive = ? WHERE id = ?", (1, id))
    conn.commit()

def handle_not_player_turn(conn):
    conn.commit()
    conn.close()
    return "It is not your turn, send a new request in like 5 seconds to see if the other bot actually made a turn", 205
