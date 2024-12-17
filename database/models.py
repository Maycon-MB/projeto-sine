from database.connection import DatabaseConnection


class CurriculoModel:
    def __init__(self, db_connection):
        """
        Inicializa o modelo de currículos com a conexão ao banco de dados.
        """
        self.db = db_connection

    def is_duplicate(self, nome, telefone):
        """
        Verifica se já existe um currículo com o mesmo nome ou telefone.
        """
        query = """
        SELECT COUNT(*)
        FROM curriculo
        WHERE nome = %s OR telefone = %s
        """
        try:
            result = self.db.execute_query(query, (nome, telefone), fetch_one=True)
            return result['count'] > 0
        except Exception as e:
            print(f"Erro ao verificar duplicidade: {e}")
            return False

    def create_tables(self):
        """
        Cria as tabelas necessárias no banco de dados, se ainda não existirem.
        """
        queries = [
            """
            CREATE TABLE IF NOT EXISTS curriculo (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                idade INT NOT NULL,
                telefone VARCHAR(20) UNIQUE NOT NULL,
                escolaridade VARCHAR(50) NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS experiencias (
                id SERIAL PRIMARY KEY,
                id_curriculo INT NOT NULL,
                cargo VARCHAR(100) NOT NULL,
                anos_experiencia INT NOT NULL,
                FOREIGN KEY (id_curriculo) REFERENCES curriculo (id) ON DELETE CASCADE
            );
            """
        ]

        for query in queries:
            try:
                self.db.execute_query(query)
            except Exception as e:
                print(f"Erro ao criar tabelas: {e}")
                raise

        # Índices para otimizar as consultas
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_curriculo_nome ON curriculo (nome);",
            "CREATE INDEX IF NOT EXISTS idx_curriculo_escolaridade ON curriculo (escolaridade);",
            "CREATE INDEX IF NOT EXISTS idx_curriculo_idade ON curriculo (idade);"
        ]

        for query in index_queries:
            try:
                self.db.execute_query(query)
            except Exception as e:
                print(f"Erro ao criar índices: {e}")
                raise

    def fetch_filtered_curriculos(self, nome=None, escolaridade=None, idade_min=None, idade_max=None):
        """
        Busca currículos com filtros otimizados utilizando a procedure do banco.
        """
        query = """
        SELECT * FROM consultar_curriculos(%s, %s, %s, %s);
        """
        params = (nome, escolaridade, idade_min, idade_max)
        try:
            return self.db.execute_query(query, params, fetch_all=True)
        except Exception as e:
            print(f"Erro ao buscar currículos: {e}")
            return []

    def insert_curriculo(self, nome, idade, telefone, escolaridade):
        """
        Insere um novo currículo no banco de dados.
        """
        query = """
        INSERT INTO curriculo (nome, idade, telefone, escolaridade)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """
        try:
            result = self.db.execute_query(query, (nome, idade, telefone, escolaridade), fetch_one=True)
            return result['id']
        except Exception as e:
            print(f"Erro ao inserir currículo: {e}")
            return None

    def insert_experiencia(self, id_curriculo, cargo, anos_experiencia):
        """
        Insere uma nova experiência profissional vinculada a um currículo.
        """
        query = """
        INSERT INTO experiencias (id_curriculo, cargo, anos_experiencia)
        VALUES (%s, %s, %s)
        RETURNING id;
        """
        try:
            result = self.db.execute_query(query, (id_curriculo, cargo, anos_experiencia), fetch_one=True)
            return result['id']
        except Exception as e:
            print(f"Erro ao inserir experiência: {e}")
            return None

    def fetch_experiencias(self, id_curriculo):
        """
        Busca as experiências profissionais associadas a um currículo.
        """
        query = """
        SELECT cargo, anos_experiencia
        FROM experiencias
        WHERE id_curriculo = %s;
        """
        try:
            return self.db.execute_query(query, (id_curriculo,), fetch_all=True)
        except Exception as e:
            print(f"Erro ao buscar experiências: {e}")
            return []

