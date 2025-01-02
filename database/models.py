from database.connection import DatabaseConnection


class CurriculoModel:
    def __init__(self, db_connection):
        """
        Inicializa o modelo de currículos com a conexão ao banco de dados.
        """
        self.db = db_connection

    def is_duplicate_nome(self, nome):
        """
        Verifica se já existe um currículo com o mesmo nome.
        """
        query = "SELECT COUNT(*) AS total FROM curriculo WHERE nome = %s"
        try:
            result = self.db.execute_query(query, (nome,), fetch_one=True)
            return result.get('total', 0) > 0
        except Exception as e:
            print(f"Erro ao verificar duplicidade do nome: {e}")
            return False

    def is_duplicate(self, nome, telefone, curriculo_id=None):
        """
        Verifica se já existe um currículo com o mesmo nome ou telefone, excluindo um ID específico.
        """
        query = """
        SELECT COUNT(*) AS total
        FROM curriculo
        WHERE (nome = %s OR telefone = %s)
        """
        params = [nome, telefone]

        if curriculo_id:
            query += " AND id != %s"
            params.append(curriculo_id)

        try:
            result = self.db.execute_query(query, tuple(params), fetch_one=True)
            return result.get('total', 0) > 0
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

    def fetch_filtered_curriculos(self, nome=None, escolaridade=None, idade_min=None, idade_max=None, cargo=None, experiencia_min=None):
        """
        Busca currículos aplicando filtros dinâmicos.
        """
        query = """
        SELECT c.id AS curriculo_id,
            c.nome,
            c.idade,
            c.telefone,
            c.escolaridade,
            e.cargo,
            e.anos_experiencia
        FROM curriculo c
        LEFT JOIN experiencias e ON c.id = e.id_curriculo
        WHERE (%s IS NULL OR c.nome ILIKE %s)
        AND (%s IS NULL OR c.escolaridade = %s)
        AND (%s IS NULL OR c.idade >= %s)
        AND (%s IS NULL OR c.idade <= %s)
        AND (%s IS NULL OR e.cargo ILIKE %s)
        AND (%s IS NULL OR e.anos_experiencia >= %s)
        """
        params = (
            nome, f"%{nome}%" if nome else None,
            escolaridade, escolaridade,
            idade_min, idade_min,
            idade_max, idade_max,
            cargo, f"%{cargo}%" if cargo else None,
            experiencia_min, experiencia_min
        )

        try:
            return self.db.execute_query(query, params, fetch_all=True)
        except Exception as e:
            print(f"Erro ao buscar currículos: {e}")
            return []

    def get_curriculo_by_id(self, curriculo_id):
        """
        Busca um currículo pelo ID.
        """
        query = "SELECT * FROM curriculo WHERE id = %s"
        try:
            return self.db.execute_query(query, (curriculo_id,), fetch_one=True)
        except Exception as e:
            print(f"Erro ao buscar currículo por ID: {e}")
            return None

    def update_curriculo(self, curriculo_id, nome, idade, telefone, escolaridade):
        """
        Atualiza os dados de um currículo.
        """
        query = """
        UPDATE curriculo
        SET nome = %s, idade = %s, telefone = %s, escolaridade = %s
        WHERE id = %s
        """
        try:
            self.db.execute_query(query, (nome, idade, telefone, escolaridade, curriculo_id))
        except Exception as e:
            print(f"Erro ao atualizar currículo: {e}")
            raise

    def insert_curriculo(self, nome, idade, telefone, escolaridade):
        """
        Insere um novo currículo no banco de dados e retorna o ID gerado.
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
            raise

    def insert_experiencias(self, id_curriculo, experiencias):
        """
        Insere experiências relacionadas a um currículo, se houver.
        """
        query = """
        INSERT INTO experiencias (id_curriculo, cargo, anos_experiencia)
        VALUES (%s, %s, %s);
        """
        try:
            for cargo, anos_experiencia in experiencias:
                self.db.execute_query(query, (id_curriculo, cargo, anos_experiencia))
        except Exception as e:
            print(f"Erro ao inserir experiências: {e}")
            raise

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
