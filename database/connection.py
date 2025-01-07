import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseConnection:
    def __init__(self, dbname, user, password, host):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host

    def connect(self):
        """
        Estabelece a conexão com o banco de dados PostgreSQL.
        """
        try:
            return psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host
            )
        except psycopg2.OperationalError as e:
            print(f"Erro de conexão: {e}")
            raise ConnectionError(f"Erro ao conectar ao banco de dados: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")
            raise ConnectionError(f"Erro ao conectar ao banco de dados: {e}")

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """
        Executa uma consulta SQL no banco de dados.
        :param query: A consulta SQL a ser executada
        :param params: Os parâmetros para a consulta
        :param fetch_one: Se `True`, retorna um único resultado
        :param fetch_all: Se `True`, retorna todos os resultados
        """
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
        except psycopg2.Error as e:
            print(f"Erro SQL: {e}")
            raise RuntimeError(f"Erro ao executar consulta: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")
            raise RuntimeError(f"Erro ao executar consulta: {e}")


