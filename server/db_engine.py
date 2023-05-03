import psycopg2
# import config

class DB:
    def __init__(self, **kwargs):
        self.conn = psycopg2.connect(user='postgres', 
                        host='172.17.0.2', port=kwargs.get('DATABASE_PORT', 5432), password='admin')

        self.cur = self.conn.cursor()
    
    def close(self, *args, **kwargs):
        self.cur.close()
        self.conn.close()
    def __del__(self):
        self.close()