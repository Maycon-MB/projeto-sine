import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseConnection:
    def __init__(self, dbname, user, password, host):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host

    def __enter__(self):
        # Inicializa a conexão e o cursor
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host
        )
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Gerencia commit e fechamento automático
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        try:
            with self as cursor:
                cursor.execute(query, params)
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
        except Exception as e:
            raise RuntimeError(f"Erro ao executar consulta: {e}")
