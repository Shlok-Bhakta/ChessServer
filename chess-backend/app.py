from flask import Flask
import time
from apscheduler.schedulers.background import BackgroundScheduler
from db_utils import *

app = Flask(__name__)

init_db()
def mytaskfunc():
    conn = get_db_connection()
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


from routes.start_game import start_game
app.add_url_rule("/start-game", view_func=start_game, methods=["POST"])

from routes.game import game
app.add_url_rule("/game", view_func=game, methods=["GET"])

from routes.move import move
app.add_url_rule("/move", view_func=move, methods=["POST"])
