import models
import psycopg2
from flask import appcontext_tearing_down
from server import app

conn = psycopg2.connect(user='postgres', 
                        host='172.17.0.2', port='5432', password='admin')

cur = conn.cursor()

def close_db_connection(sender, **extra):
    cur.close()
    conn.close()

appcontext_tearing_down.connect(close_db_connection, app)

# cur.execute('')

# cur.close()
# conn.close()

