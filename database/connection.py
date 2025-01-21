import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseConnection:
    def __init__(self, dbname, user, password, host, port=5432):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port  # 🔥 Adiciona a porta

    def connect(self):
        """
        Estabelece a conexão com o banco de dados PostgreSQL.
        """
        try:
            return psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
        except psycopg2.OperationalError as e:
            print(f"❌ Erro de conexão: {e}")
            raise ConnectionError(f"Erro ao conectar ao banco de dados: {e}")
 
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """
        Executa uma consulta SQL no banco de dados.
        """
        try:
            with self.connect() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:  # RealDictCursor retorna dicionários
                    cursor.execute(query, params)
                    if fetch_one:
                        result = cursor.fetchone()
                    elif fetch_all:
                        result = cursor.fetchall()
                    else:
                        result = None

                    # Realiza commit se necessário
                    if query.strip().lower().startswith(("insert", "update", "delete")):
                        conn.commit()

                    return result

        except Exception as e:
            print(f"Erro ao executar consulta: {e}")
            raise

