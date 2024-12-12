import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseConnection:
    def __init__(self, dbname, user, password, host):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host

    def connect(self):
        try:
            return psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host
            )
        except Exception as e:
            raise ConnectionError(f"Erro ao conectar ao banco de dados: {e}")

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        try:
            conn = self.connect()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                result = None

            conn.commit()
            cursor.close()
            conn.close()
            return result
        except Exception as e:
            raise RuntimeError(f"Erro ao executar consulta: {e}")
