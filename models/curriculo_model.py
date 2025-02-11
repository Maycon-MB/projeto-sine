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
        if not telefone:
            return False
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
        if not telefone:
            return None
        return re.sub(r"\D", "", telefone)
    
    def listar_funcao(self):
        """
        Lista todas as funções (cargos) disponíveis na tabela public.funcoes.
        """
        query = "SELECT nome FROM public.funcoes ORDER BY nome;"

        try:
            results = self.db.execute_query(query, fetch_all=True)
            # Converter cada resultado para um dicionário e acessar o campo 'nome'
            funcoes = [result['nome'] for result in results]
            return funcoes
        except Exception as e:
            print(f"Erro ao listar funções: {e}")
            return []

    def obter_funcao_id(self, funcao_nome):
        """
        Busca o ID da função no banco de dados pelo nome da função.
        """
        query = "SELECT id FROM public.funcoes WHERE nome = %s;"

        try:
            resultado = self.db.execute_query(query, (funcao_nome,), fetch_one=True)
            if resultado:
                return resultado['id']
            return None
        except Exception as e:
            print(f"Erro ao buscar ID da função: {e}")
            raise

        
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

    def fetch_curriculos(self, filtros, limite=10, offset=0):
        """
        Busca currículos aplicando filtros dinâmicos, ordenação por nome e paginação.
        """
        query = """
            SELECT * FROM public.filtrar_curriculos(
                %(nome)s::TEXT, 
                %(cidade)s::TEXT, 
                %(escolaridade)s::TEXT, 
                %(funcao)s::TEXT,  -- Ajustado para "funcao"
                %(tem_ctps)s::BOOLEAN, 
                %(servico)s::TEXT, 
                %(idade_min)s::INTEGER, 
                %(idade_max)s::INTEGER, 
                %(experiencia_min)s::INTEGER, 
                %(experiencia_max)s::INTEGER, 
                %(sexo)s::TEXT, 
                %(cpf)s::TEXT, 
                %(cep)s::TEXT, 
                %(pcd)s::BOOLEAN, 
                %(telefone)s::TEXT, 
                %(telefone_extra)s::TEXT, 
                %(limite)s::INTEGER, 
                %(offset)s::INTEGER
            )
            ORDER BY nome ASC;
        """
        # Parâmetros de filtro
        params = {
            "nome": filtros.get("nome"),
            "cidade": filtros.get("cidade"),
            "escolaridade": filtros.get("escolaridade"),
            "funcao": filtros.get("funcao"),  # "funcao" é agora o filtro correto
            "tem_ctps": filtros.get("tem_ctps"),
            "servico": filtros.get("servico"),
            "idade_min": filtros.get("idade_min"),
            "idade_max": filtros.get("idade_max"),
            "experiencia_min": filtros.get("experiencia_min"),
            "experiencia_max": filtros.get("experiencia_max"),
            "sexo": filtros.get("sexo"),
            "cpf": filtros.get("cpf"),
            "cep": filtros.get("cep"),
            "pcd": filtros.get("pcd"),  # "pcd" continua como filtro
            "telefone": filtros.get("telefone", ""),  # Parâmetro de telefone
            "telefone_extra": filtros.get("telefone_extra", ""),  # Parâmetro de telefone_extra
            "limite": limite,
            "offset": offset,
        }
        
        # Executa a consulta
        return self.db.execute_query(query, params, fetch_all=True)

    def get_curriculo_by_id(self, curriculo_id):
        """
        Busca um único currículo pelo ID, incluindo experiências associadas.
        """
        query = """
        SELECT c.id AS curriculo_id, c.nome, c.cpf, c.sexo, c.data_nascimento, ci.nome AS cidade, 
            c.telefone, c.telefone_extra, c.escolaridade, c.servico, 
            c.cep, c.pcd, c.tem_ctps, -- Incluindo os novos campos
            e.funcao, e.anos_experiencia, e.meses_experiencia
        FROM curriculo c
        LEFT JOIN experiencias e ON c.id = e.id_curriculo
        LEFT JOIN cidades ci ON c.cidade_id = ci.id
        WHERE c.id = %s;
        """
        try:
            return self.db.execute_query(query, (curriculo_id,), fetch_one=True)
        except Exception as e:
            print(f"Erro ao buscar currículo por ID: {e}")
            return None

    def update_curriculo(self, curriculo_id, nome, cpf, sexo, data_nascimento, cidade_id, telefone, telefone_extra, escolaridade, tem_ctps, servico, cep, pcd):
        """
        Atualiza os dados de um currículo.
        """
        cpf = self.limpar_formatacao_cpf(cpf)
        telefone = self.limpar_formatacao_telefone(telefone)
        telefone_extra = self.limpar_formatacao_telefone(telefone_extra) if telefone_extra else None

        if not self.validar_cpf(cpf):
            raise ValueError("CPF inválido. Deve conter 11 dígitos numéricos.")
        if not self.validar_telefone(telefone):
            raise ValueError("Telefone inválido. Deve conter 10 ou 11 dígitos.")
        if cep:
            cep = re.sub(r"\D", "", cep)  # Remove caracteres não numéricos
            if len(cep) != 8:
                raise ValueError("CEP inválido. Deve conter exatamente 8 dígitos numéricos.")

        query = """
        UPDATE curriculo
        SET nome = %s, cpf = %s, sexo = %s, data_nascimento = %s, cidade_id = %s,
            telefone = %s, telefone_extra = %s, escolaridade = %s,
            tem_ctps = %s, servico = %s, cep = %s, pcd = %s
        WHERE id = %s;
        """
        try:
            self.db.execute_query(
                query,
                (nome, cpf, sexo, data_nascimento, cidade_id, telefone, telefone_extra, escolaridade, tem_ctps, servico, cep, pcd, curriculo_id)
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

    def insert_curriculo(self, nome, cpf, sexo, data_nascimento, cidade_id, telefone, telefone_extra, escolaridade, tem_ctps, experiencias, servico, cep, pcd):
        """
        Insere um novo currículo no banco de dados, incluindo as experiências.
        """
        # Limpa e valida o CPF, telefones e CEP
        cpf = self.limpar_formatacao_cpf(cpf)
        telefone = self.limpar_formatacao_telefone(telefone)
        telefone_extra = self.limpar_formatacao_telefone(telefone_extra) if telefone_extra else None
        cep = re.sub(r'\D', '', cep)  # Remove caracteres não numéricos do CEP

        if not self.validar_cpf(cpf):
            raise ValueError("CPF inválido. Deve conter 11 dígitos numéricos.")
        if not self.validar_telefone(telefone):
            raise ValueError("Telefone inválido. Deve conter 10 ou 11 dígitos.")
        if len(cep) != 8:  # Verifica se o CEP contém exatamente 8 dígitos
            raise ValueError("CEP inválido. Deve conter exatamente 8 dígitos numéricos.")

        # Insere os dados do currículo
        query_curriculo = """
        INSERT INTO curriculo (nome, cpf, sexo, data_nascimento, cidade_id, telefone, telefone_extra, escolaridade, tem_ctps, servico, cep, pcd)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        try:
            curriculo_id = self.db.execute_query(
                query_curriculo,
                (nome, cpf, sexo, data_nascimento, cidade_id, telefone, telefone_extra, escolaridade, tem_ctps, servico, cep, pcd),
                fetch_one=True
            )['id']

            # Insere as experiências, se houver
            if experiencias:
                query_experiencia = """
                INSERT INTO experiencias (id_curriculo, funcao_id, anos_experiencia, meses_experiencia)
                VALUES (%s, %s, %s, %s);
                """
                for experiencia in experiencias:
                    funcao, anos, meses = experiencia
                    self.db.execute_query(query_experiencia, (curriculo_id, funcao, anos, meses))

            return curriculo_id
        except Exception as e:
            print(f"Erro ao inserir currículo: {e}")
            raise

    def insert_experiencias(self, id_curriculo, experiencias):
        """
        Insere ou atualiza experiências profissionais associadas a um currículo.
        """
        query = """
        INSERT INTO experiencias (id_curriculo, funcao, anos_experiencia, meses_experiencia)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id_curriculo, funcao)
        DO UPDATE SET
            anos_experiencia = EXCLUDED.anos_experiencia,
            meses_experiencia = EXCLUDED.meses_experiencia;
        """
        for funcao, anos_experiencia, meses_experiencia in experiencias:
            if not funcao or anos_experiencia < 0 or meses_experiencia < 0 or meses_experiencia >= 12:
                raise ValueError("Experiência inválida. Preencha todos os campos corretamente.")
            self.db.execute_query(query, (id_curriculo, funcao, anos_experiencia, meses_experiencia))

    def fetch_experiencias(self, id_curriculo):
        """
        Busca as experiências profissionais associadas a um currículo.
        """
        query = """
        SELECT funcao, anos_experiencia, meses_experiencia
        FROM experiencias
        WHERE id_curriculo = %s;
        """
        try:
            return self.db.execute_query(query, (id_curriculo,), fetch_all=True)
        except Exception as e:
            print(f"Erro ao buscar experiências: {e}")
            return []

    def get_curriculos_por_cidade(self, filtro=None):
        """
        Retorna um dicionário com a contagem de currículos por cidade.
        Se um filtro for passado, aplica a lógica correspondente.
        """
        query = "SELECT ci.nome, COUNT(c.id) FROM curriculo c JOIN cidades ci ON c.cidade_id = ci.id"

        # Aplicar filtro de data (PostgreSQL)
        filtros = {
            "Últimos 30 dias": " WHERE c.data_cadastro >= NOW() - INTERVAL '30 days'",
            "Últimos 6 meses": " WHERE c.data_cadastro >= NOW() - INTERVAL '6 months'",
            "Último ano": " WHERE c.data_cadastro >= NOW() - INTERVAL '1 year'"
        }

        if filtro in filtros:
            query += filtros[filtro]

        query += " GROUP BY ci.nome;"
        
        try:
            results = self.db.execute_query(query, fetch_all=True)
            return {row['nome']: row['count'] for row in results}
        except Exception as e:
            print(f"Erro ao obter currículos por cidade: {e}")
            return {}

    def get_escolaridade_distribuicao(self, filtro=None):
        """
        Retorna um dicionário com a distribuição de escolaridade, aplicando filtros se necessário.
        """
        query = "SELECT escolaridade, COUNT(id) AS total FROM curriculo"
        
        # Aplicar filtro de data (PostgreSQL)
        filtros = {
            "Últimos 30 dias": " WHERE data_cadastro >= NOW() - INTERVAL '30 days'",
            "Últimos 6 meses": " WHERE data_cadastro >= NOW() - INTERVAL '6 months'",
            "Último ano": " WHERE data_cadastro >= NOW() - INTERVAL '1 year'"
        }
        
        if filtro in filtros:
            query += filtros[filtro]
        
        query += " GROUP BY escolaridade;"

        try:
            results = self.db.execute_query(query, fetch_all=True)
            return {row['escolaridade']: row['total'] for row in results}
        except Exception as e:
            print(f"Erro ao obter distribuição de escolaridade: {e}")
            return {}

    def get_top_funcoes(self, filtro=None, limit=5):
        """
        Retorna os funcaos mais populares com base na contagem de currículos, aplicando filtros se necessário.
        """
        query = """
        SELECT experiencias.funcao, COUNT(experiencias.id_curriculo) AS total
        FROM experiencias
        """
        
        # Aplicar filtro de data baseado na tabela de currículos (PostgreSQL)
        filtros = {
            "Últimos 30 dias": " JOIN curriculo c ON experiencias.id_curriculo = c.id WHERE c.data_cadastro >= NOW() - INTERVAL '30 days'",
            "Últimos 6 meses": " JOIN curriculo c ON experiencias.id_curriculo = c.id WHERE c.data_cadastro >= NOW() - INTERVAL '6 months'",
            "Último ano": " JOIN curriculo c ON experiencias.id_curriculo = c.id WHERE c.data_cadastro >= NOW() - INTERVAL '1 year'"
        }
        
        if filtro in filtros:
            query += filtros[filtro]
        
        query += " GROUP BY experiencias.funcao ORDER BY total DESC LIMIT %s;"

        try:
            results = self.db.execute_query(query, (limit,), fetch_all=True)
            return {row['funcao']: row['total'] for row in results}
        except Exception as e:
            print(f"Erro ao obter top funcaos: {e}")
            return {}

    def get_pcd_distribuicao(self, filtro=None):
        """
        Retorna a distribuição entre pessoas que estão buscando o pcd e as que já possuem experiência, aplicando filtros se necessário.
        """
        query = """
        SELECT 
            CASE 
                WHEN pcd THEN 'pcd'
                ELSE 'Com Experiência'
            END AS categoria,
            COUNT(*) AS total
        FROM curriculo
        """

        # Aplicar filtro de data (PostgreSQL)
        filtros = {
            "Últimos 30 dias": " WHERE data_cadastro >= NOW() - INTERVAL '30 days'",
            "Últimos 6 meses": " WHERE data_cadastro >= NOW() - INTERVAL '6 months'",
            "Último ano": " WHERE data_cadastro >= NOW() - INTERVAL '1 year'"
        }
        
        if filtro in filtros:
            query += filtros[filtro]
        
        query += " GROUP BY categoria;"

        try:
            results = self.db.execute_query(query, fetch_all=True)
            return {row['categoria']: row['total'] for row in results}
        except Exception as e:
            print(f"Erro ao obter distribuição de pcd: {e}")
            return {}

    def get_experiencia_por_idade(self, filtro=None):
        """
        Retorna um dicionário com a distribuição de experiência por idade.
        """
        query = """
        SELECT
            FLOOR(DATE_PART('year', AGE(c.data_nascimento))) AS idade,
            SUM(e.anos_experiencia) AS experiencia_total
        FROM curriculo c
        JOIN experiencias e ON c.id = e.id_curriculo
        """
        
        filtros = {
            "Últimos 30 dias": " WHERE c.data_cadastro >= NOW() - INTERVAL '30 days'",
            "Últimos 6 meses": " WHERE c.data_cadastro >= NOW() - INTERVAL '6 months'",
            "Último ano": " WHERE c.data_cadastro >= NOW() - INTERVAL '1 year'"
        }
        
        if filtro in filtros:
            query += filtros[filtro]
        
        query += " GROUP BY idade ORDER BY idade;"
        
        try:
            results = self.db.execute_query(query, fetch_all=True)
            return {row['idade']: row['experiencia_total'] for row in results}
        except Exception as e:
            print(f"Erro ao obter distribuição de experiência por idade: {e}")
            return {}
