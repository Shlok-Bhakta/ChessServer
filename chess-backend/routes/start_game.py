from flask import request
from db_utils import * 

def start_game():
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
    player_id = create_user_and_get_id(conn, player_name)
    bot_id = create_bot_and_get_id(conn, bot_name, player_id)
    if bot_id == -1:
        conn.commit()
        conn.close()
        return "Bot name does not belong to the player please pick a different name or pick a name that you own", 400

    # check if player&bot are currently in a game if so return a 202
    cursor = conn.execute("SELECT * FROM game WHERE (whiteplayerid = ? OR blackplayerid = ?) AND (whitebotid = ? OR blackbotid = ?) AND isactive != -1", (player_id, player_id, bot_id, bot_id))
    row = cursor.fetchone()
    if row:
        conn.commit()
        conn.close()
        return f"You are currently in a game, why are you hitting this endpoint?", 202

    # check if bot is already in the queue
    cursor = conn.execute("SELECT * FROM queue WHERE botid = ?", (bot_id,))
    row = cursor.fetchone()
    if row:
        # extend the timer
        conn.execute("UPDATE queue SET lastseen = ? WHERE id = ?", (int(round(time.time() * 1000)), row[0]))
        conn.commit()
        conn.close()
        return "Timout timer extended. You have 20 seconds to send another request or you will be kicked from the queue", 200

    conn.commit()    

    # see if the bot has a preffered opponent
    if payload.get("opponent"):
        opponent = payload.get("opponent")
        # check if the opponent is in the queue
        opponent_bot_id = get_bot_id_from_name(conn, opponent)
        if opponent_bot_id == -1:
            conn.commit()
            conn.close()
            return "Opponent does not exist in the database. Please call this api again and maybe the opponent will exist by then", 400
        # check if the opponent is already in the queue
        cursor = conn.execute("SELECT * FROM queue WHERE botid = ?", (opponent_bot_id,))
        row = cursor.fetchone()
        if row:
            # opponent is in the queue so we can start the game by deleting the queue entry
            opponent_player_id = row[1]

            conn.execute("DELETE FROM queue WHERE id = ?", (row[0],))
            conn.commit()
            init_game(conn, player_id, opponent_player_id, bot_id, opponent_bot_id)
            cursor = conn.execute("SELECT * FROM player WHERE id = ?", (opponent_player_id,))
            row = cursor.fetchone()

            cursor = conn.execute("SELECT * FROM bot WHERE id = ?", (opponent_bot_id,))
            botrow = cursor.fetchone()
            conn.close()
            return f"Game Started with opponent {row[1]} and bot {botrow[2]}", 202
        else:
            conn.execute("INSERT INTO queue (id, playerid, botid, lastseen) VALUES (NULL, ?, ?, ?)", (player_id, bot_id, int(round(time.time() * 1000))))
            conn.commit()
            conn.close()
            return "Your preffered opponent is not in the queue, you have been added to the queue", 400
    else:
        # pair with the first bot (oldest) when reading the queue
        cursor = conn.execute("SELECT * FROM queue")
        row = cursor.fetchone()
        if row:
            opponent_player_id = row[1]
            opponent_bot_id = row[2]
            init_game(conn, player_id, opponent_player_id, bot_id, opponent_bot_id)
            
            cursor = conn.execute("SELECT * FROM player WHERE id = ?", (opponent_player_id,))
            row = cursor.fetchone() 

            cursor = conn.execute("SELECT * FROM bot WHERE id = ?", (opponent_bot_id,))
            botrow = cursor.fetchone()
            conn.close()
            return f"Game Started with opponent {row[1]} and bot {botrow[2]}", 202

    # add bot to the queue
    conn.execute("INSERT INTO queue (id, playerid, botid, lastseen) VALUES (NULL, ?, ?, ?)", (player_id, bot_id, int(round(time.time() * 1000))))
    conn.commit()
    conn.close()
    return f"No bots currently in the queue. You have been added to the queue", 200