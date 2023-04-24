import psycopg2

# import sys

class DB:
    def __init__(self):
        self.conn = psycopg2.connect(user='postgres', 
                        host='172.17.0.2', port='5432', password='admin')

        self.cur = self.conn.cursor()
        # print(self.conn, self.cur, file=sys.stderr)
    
    def close(self, sender, **extra):
        # print('close', file=sys.stderr)
        # print(sender, extra, file=sys.stderr)
        self.cur.close()
        self.conn.close()