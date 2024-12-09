import psycopg2

class DB:
    def __init__(self, **kwargs):
        self.conn = psycopg2.connect(
            user = kwargs['DATABASE_USER'],
            password = kwargs['DATABASE_PASSWORD'],
            host = kwargs['DATABASE_HOST'],
            port = kwargs['DATABASE_PORT']
        )

        self.cur = self.conn.cursor()
    
    def close(self, *args, **kwargs):
        self.cur.close()
        self.conn.close()
    def __del__(self):
        self.close()
