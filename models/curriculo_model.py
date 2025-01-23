from database.connection import DatabaseConnection
import re

class CurriculoModel:
    def __init__(self, db_connection):
        """
        Inicializa o modelo de currículos com a conexão ao banco de dados.
        """
        self.db = db_connection

    @staticmethod
    def validar_telefone(telefone):
        """
        Valida se o telefone contém apenas números com 10 ou 11 dígitos.
        """
        pattern = r"^\d{10,11}$"
        return re.match(pattern, telefone)
    
    @staticmethod
    def validar_cpf(cpf):
        """
        Valida se o CPF contém apenas 11 dígitos numéricos.
        """
        pattern = r"^\d{11}$"
        return re.match(pattern, cpf)
    
    @staticmethod
    def limpar_formatacao_cpf(cpf):
        """
        Remove caracteres especiais do CPF, deixando apenas os números.
        """
        return re.sub(r"\D", "", cpf)

    @staticmethod
    def limpar_formatacao_telefone(telefone):
        """
        Remove caracteres especiais do telefone, deixando apenas os números.
        """
        return re.sub(r"\D", "", telefone)
        
    def listar_cidades(self):
        """
        Lista todas as cidades disponíveis.
        """
        query = "SELECT nome FROM cidades ORDER BY nome;"
        try:
            results = self.db.execute_query(query, fetch_all=True)
            # Converter cada resultado para um dicionário e acessar o campo 'nome'
            cidades = [result['nome'] for result in results]
            return cidades
        except Exception as e:
            print(f"Erro ao listar cidades: {e}")
            return []

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

    def is_duplicate(self, cpf):
        """
        Verifica se já existe um currículo com o mesmo CPF.
        """
        query = "SELECT COUNT(*) AS total FROM curriculo WHERE cpf = %s"
        try:
            result = self.db.execute_query(query, (cpf,), fetch_one=True)
            return result.get('total', 0) > 0
        except Exception as e:
            print(f"Erro ao verificar duplicidade de CPF: {e}")
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

    def fetch_curriculos(self, filtros, limite=10, offset=0):
        """
        Busca currículos aplicando filtros dinâmicos e paginação.
        """
        query = """
            SELECT * FROM filtrar_curriculos(
                %(nome)s, %(cidade)s, %(escolaridade)s, %(cargo)s, 
                %(vaga_encaminhada)s, %(tem_ctps)s, %(servico)s, 
                %(idade_min)s, %(idade_max)s, %(experiencia_min)s, %(experiencia_max)s,
                %(sexo)s, %(cpf)s, %(limite)s, %(offset)s
            );
        """
        params = {
            "nome": filtros.get("nome"),
            "cidade": filtros.get("cidade"),
            "escolaridade": filtros.get("escolaridade"),
            "cargo": filtros.get("cargo"),
            "vaga_encaminhada": filtros.get("vaga_encaminhada"),
            "tem_ctps": filtros.get("tem_ctps"),
            "servico": filtros.get("servico"),
            "idade_min": filtros.get("idade_min"),
            "idade_max": filtros.get("idade_max"),
            "experiencia_min": filtros.get("experiencia_min"),  # Passar experiência mínima
            "experiencia_max": filtros.get("experiencia_max"),  # Passar experiência máxima
            "sexo": filtros.get("sexo"),
            "cpf": filtros.get("cpf"),
            "limite": limite,
            "offset": offset,
        }
        return self.db.execute_query(query, params, fetch_all=True)

    def get_curriculo_by_id(self, curriculo_id):
        """
        Busca um único currículo pelo ID, incluindo experiências associadas.
        """
        query = """
        SELECT c.id AS curriculo_id, c.nome, c.cpf, c.sexo, c.data_nascimento, ci.nome AS cidade, 
            c.telefone, c.telefone_extra, c.escolaridade, c.servico, c.vaga_encaminhada, 
            e.cargo, e.anos_experiencia, e.meses_experiencia
        FROM curriculo c
        LEFT JOIN experiencias e ON c.id = e.id_curriculo
        LEFT JOIN cidades ci ON c.cidade_id = ci.id
        WHERE c.id = %s;
        """
        try:
            # Alterar para fetch_one
            return self.db.execute_query(query, (curriculo_id,), fetch_one=True)
        except Exception as e:
            print(f"Erro ao buscar currículo por ID: {e}")
            return None


    def update_curriculo(self, curriculo_id, nome, cpf, sexo, data_nascimento, cidade_id, telefone, telefone_extra, escolaridade, vaga_encaminhada, tem_ctps, servico):
        """
        Atualiza os dados de um currículo.
        """
        # Limpa e valida o CPF e telefones
        cpf = self.limpar_formatacao_cpf(cpf)
        telefone = self.limpar_formatacao_telefone(telefone)
        telefone_extra = self.limpar_formatacao_telefone(telefone_extra) if telefone_extra else None

        if not self.validar_cpf(cpf):
            raise ValueError("CPF inválido. Deve conter 11 dígitos numéricos.")
        if not self.validar_telefone(telefone):
            raise ValueError("Telefone inválido. Deve conter 10 ou 11 dígitos.")

        query = """
        UPDATE curriculo
        SET nome = %s, cpf = %s, sexo = %s, data_nascimento = %s, cidade_id = %s,
            telefone = %s, telefone_extra = %s, escolaridade = %s, vaga_encaminhada = %s,
            tem_ctps = %s, servico = %s
        WHERE id = %s;
        """
        try:
            self.db.execute_query(
                query,
                (nome, cpf, sexo, data_nascimento, cidade_id, telefone, telefone_extra, escolaridade, vaga_encaminhada, tem_ctps, servico, curriculo_id)
            )
        except Exception as e:
            print(f"Erro ao atualizar currículo: {e}")
            raise

    def obter_cidade_id(self, cidade_nome):
        """
        Busca o ID da cidade no banco de dados pelo nome da cidade.
        """
        query = "SELECT id FROM cidades WHERE nome = %s;"
        try:
            resultado = self.db.execute_query(query, (cidade_nome,), fetch_one=True)
            if resultado:
                return resultado['id']
            return None
        except Exception as e:
            print(f"Erro ao buscar ID da cidade: {e}")
            raise

    def insert_curriculo(self, nome, cpf, sexo, data_nascimento, cidade_id, telefone, telefone_extra, escolaridade, vaga_encaminhada, tem_ctps, experiencias, servico):
        """
        Insere um novo currículo no banco de dados, incluindo as experiências.
        """
        # Limpa e valida o CPF e telefones
        cpf = self.limpar_formatacao_cpf(cpf)
        telefone = self.limpar_formatacao_telefone(telefone)
        telefone_extra = self.limpar_formatacao_telefone(telefone_extra) if telefone_extra else None

        if not self.validar_cpf(cpf):
            raise ValueError("CPF inválido. Deve conter 11 dígitos numéricos.")
        if not self.validar_telefone(telefone):
            raise ValueError("Telefone inválido. Deve conter 10 ou 11 dígitos.")

        # Insere os dados do currículo
        query_curriculo = """
        INSERT INTO curriculo (nome, cpf, sexo, data_nascimento, cidade_id, telefone, telefone_extra, escolaridade, vaga_encaminhada, tem_ctps, servico)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        try:
            curriculo_id = self.db.execute_query(
                query_curriculo,
                (nome, cpf, sexo, data_nascimento, cidade_id, telefone, telefone_extra, escolaridade, vaga_encaminhada, tem_ctps, servico),
                fetch_one=True
            )['id']

            # Insere as experiências, se houver
            if experiencias:
                query_experiencia = """
                INSERT INTO experiencias (id_curriculo, cargo, anos_experiencia, meses_experiencia)
                VALUES (%s, %s, %s, %s);
                """
                for experiencia in experiencias:
                    cargo, anos, meses = experiencia
                    self.db.execute_query(query_experiencia, (curriculo_id, cargo, anos, meses))

            return curriculo_id
        except Exception as e:
            print(f"Erro ao inserir currículo: {e}")
            raise

    def insert_experiencias(self, id_curriculo, experiencias):
        """
        Insere ou atualiza experiências profissionais associadas a um currículo.
        """
        query = """
        INSERT INTO experiencias (id_curriculo, cargo, anos_experiencia, meses_experiencia)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id_curriculo, cargo)
        DO UPDATE SET
            anos_experiencia = EXCLUDED.anos_experiencia,
            meses_experiencia = EXCLUDED.meses_experiencia;
        """
        for cargo, anos_experiencia, meses_experiencia in experiencias:
            if not cargo or anos_experiencia < 0 or meses_experiencia < 0 or meses_experiencia >= 12:
                raise ValueError("Experiência inválida. Preencha todos os campos corretamente.")
            self.db.execute_query(query, (id_curriculo, cargo, anos_experiencia, meses_experiencia))

    def fetch_experiencias(self, id_curriculo):
        """
        Busca as experiências profissionais associadas a um currículo.
        """
        query = """
        SELECT cargo, anos_experiencia, meses_experiencia
        FROM experiencias
        WHERE id_curriculo = %s;
        """
        try:
            return self.db.execute_query(query, (id_curriculo,), fetch_all=True)
        except Exception as e:
            print(f"Erro ao buscar experiências: {e}")
            return []

