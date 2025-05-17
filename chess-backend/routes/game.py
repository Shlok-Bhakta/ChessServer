from flask import request
from db_utils import *

def game():
    conn = get_db_connection()
    # expected format {'player_name': 'shlok', 'bot_name': 'LazySuzan', 'move': 'e2e4}
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

    # prepare the game and send back the responses
    # check if the game is over
    if(row["isactive"] == -1):
        return "The game is over", 205    
    # check if it is the current bots turn
    if row["isactive"] == 1: # white player goes
        # check if the current bot is the white bot
        if row["whitebotid"] == bot_id:
            board = reconstruct_board(row["moves"])

            current_board = board.fen().split(" ")[0]
            # update the request sent time
            conn.execute("UPDATE game SET requestsent = ? WHERE id = ?", (time.time(), row["id"]))
            conn.commit()
            conn.close()
            return {
                "move_number": len(row["moves"].split(",")),
                "current_board": current_board,
                "time_remaining": row["whiteplayertime"],
                "color": "white"
            }
        else:
            conn.commit()
            conn.close()
            return "It is not your turn, send a new request in like 5 seconds to see if the other bot actually made a turn", 205
    if row["isactive"] == 2: # black player goes 
        # check if the current bot is the black bot
        if row["blackbotid"] == bot_id:
            board = reconstruct_board(row["moves"])

            current_board = board.fen().split(" ")[0]
            # update the request sent time
            conn.execute("UPDATE game SET requestsent = ? WHERE id = ?", (time.time(), row["id"]))
            conn.commit()
            conn.close()
            return {
                "move_number": len(row["moves"].split(",")),
                "current_board": current_board,
                "time_remaining": row["blackplayertime"],
                "color": "black"
            }
        else:
            conn.commit()
            conn.close()
            return "It is not your turn, send a new request in like 5 seconds to see if the other bot actually made a turn", 205

    conn.commit()
    conn.close()
    return f"hi here is your payload {payload} you are player {player_id} and bot {bot_id}", 200