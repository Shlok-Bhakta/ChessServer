from flask import request
import chess
from db_utils import *

def move():
    call_time = time.time()
    conn = get_db_connection()
    # expected format {'player_name': 'shlok', 'bot_name': 'LazySuzan'}
    payload = request.get_json()
    # validate the payload
    if not payload:
        conn.commit()
        conn.close()
        return "No payload", 400
    if not payload.get("player_name") and not payload.get("bot_name"):
        conn.commit()
        conn.close()
        return "No player_name or bot_name", 400
    if not payload.get("player_name"):
        conn.commit()
        conn.close()
        return "No player_name", 400
    if not payload.get("bot_name"):
        conn.commit()
        conn.close()
        return "No bot_name", 400

    player_name = payload.get("player_name")
    bot_name = payload.get("bot_name")
    player_id = get_user_id_from_name(conn, player_name)
    bot_id = get_bot_id_from_name(conn, bot_name)
    if player_id == -1:
        conn.commit()
        conn.close()
        return "Player does not exist? make sure you dont have any typos in the name", 400
    if bot_id == -1:
        conn.commit()
        conn.close()
        return "The bot does not exist? make sure you dont have any typos", 400
    if check_bot_ownership(conn, bot_id, player_id) == -1:
        conn.commit()
        conn.close()
        return "The bot does not belong to the player? make sure you dont have any typos", 400
    
    # check if player&bot are currently in a game
    cursor = conn.execute("SELECT * FROM game WHERE (whiteplayerid = ? OR blackplayerid = ?) AND (whitebotid = ? OR blackbotid = ?)", (player_id, player_id, bot_id, bot_id))
    row = cursor.fetchone() # current game row from the db
    if not row:
        conn.commit()
        conn.close()
        return "You are not in a game", 400

    # check if the game is over
    if(row["isactive"] == -1):
        return "The game is over", 205    
    # check if it is the current bots turn
    if row["isactive"] == 1: # white player goes
        # check if the current bot is the white bot
        if row["whitebotid"] == bot_id:
            # get the most recent fen
            fen_arr = row["moves"].split(",")
            current_board = fen_arr[-1]
            # get the move back from the payload
            move_val = payload.get("move")
            board = chess.Board(current_board)
            board.turn = chess.WHITE
            # TODO proper validation of the move
            move = chess.Move.from_uci(move_val)
            board.push(move)
            fen = board.fen()
            
            fen_arr.append(fen.split(" ")[0])
            fen_string = ','.join(fen_arr)
            # update fen string
            conn.execute("UPDATE game SET moves = ? WHERE id = ?", (fen_string, row["id"]))
            # update the time left for white
            conn.execute("UPDATE game SET whiteplayertime = ? WHERE id = ?", (row["whiteplayertime"] - (call_time - row["requestsent"]), row["id"]))
            # update isactive to be 2 (black turn)
            conn.execute("UPDATE game SET isactive = ? WHERE id = ?", (2, row["id"]))
            conn.commit()
            conn.close()
            return "Game updated", 200
        else:
            conn.commit()
            conn.close()
            return "It is not your turn, send a new request in like 5 seconds to see if the other bot actually made a turn", 205
    if row["isactive"] == 2: # black player goes
        # check if the current bot is the black bot
        if row["blackbotid"] == bot_id:
            # get the most recent fen
            fen_arr = row["moves"].split(",")
            current_board = fen_arr[-1]
            # get the move back from the payload
            move_val = payload.get("move")
            board = chess.Board(current_board)
            board.turn = chess.BLACK
            # TODO proper validation of the move
            move = chess.Move.from_uci(move_val)
            board.push(move)
            fen = board.fen()
            fen_arr.append(fen.split(" ")[0])
            fen_string = ','.join(fen_arr)
            # update fen string
            conn.execute("UPDATE game SET moves = ? WHERE id = ?", (fen_string, row["id"]))
            # update the time left for black
            conn.execute("UPDATE game SET blackplayertime = ? WHERE id = ?", (row["blackplayertime"] - (call_time - row["requestsent"]), row["id"]))
            # update isactive to be 1 (white turn)
            conn.execute("UPDATE game SET isactive = ? WHERE id = ?", (1, row["id"]))
            conn.commit()
            conn.close()
            return "Game updated", 205
        else:
            conn.commit()
            conn.close()
            return "It is not your turn", 400

    conn.commit()
    conn.close()
    return f"hi here is your payload {payload} you are player {player_id} and bot {bot_id}", 200