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
        Sempre consulta a tabela para garantir a lista mais atualizada.
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

    def fetch_curriculos(self, filtros):
        query = """
            SELECT 
                curriculo_id,
                cpf,
                nome,
                idade,
                COALESCE(telefone, '') AS telefone,       -- Converte NULL para ''
                COALESCE(telefone_extra, '') AS telefone_extra,
                cidade,
                escolaridade,
                tem_ctps,
                COALESCE(cep, '') AS cep,                 -- Converte NULL para ''
                pcd,
                funcao,
                anos_experiencia,
                meses_experiencia
            FROM public.filtrar_curriculos(
                %(nome)s::TEXT, 
                %(cidade)s::TEXT, 
                %(escolaridade)s::TEXT, 
                %(funcao)s::TEXT,  
                %(tem_ctps)s::BOOLEAN, 
                %(idade_min)s::INTEGER, 
                %(idade_max)s::INTEGER, 
                %(experiencia)s::INTEGER,
                %(sexo)s::TEXT, 
                %(cpf)s::TEXT, 
                %(cep)s::TEXT, 
                %(pcd)s::BOOLEAN, 
                %(telefone)s::TEXT, 
                %(telefone_extra)s::TEXT
            )
            ORDER BY nome ASC;
        """        
        # Parâmetros de filtro
        params = {
            "nome": filtros.get("nome"),
            "cidade": filtros.get("cidade"),
            "escolaridade": filtros.get("escolaridade"),
            "funcao": filtros.get("funcao"),
            "tem_ctps": filtros.get("tem_ctps"),
            "idade_min": filtros.get("idade_min"),
            "idade_max": filtros.get("idade_max"),
            "experiencia": filtros.get("experiencia"),  # Agora está correto!
            "sexo": filtros.get("sexo"),
            "cpf": filtros.get("cpf"),
            "cep": filtros.get("cep"),
            "pcd": filtros.get("pcd"),
            "telefone": filtros.get("telefone", ""),
            "telefone_extra": filtros.get("telefone_extra", "")
        }
        
        # Executa a consulta
        return self.db.execute_query(query, params, fetch_all=True)

    def get_curriculo_by_id(self, curriculo_id):
        """
        Busca um único currículo pelo ID, incluindo experiências associadas.
        """
        query = """
        SELECT c.id AS curriculo_id, c.nome, c.cpf, c.sexo, c.data_nascimento, ci.nome AS cidade, 
            c.telefone, c.telefone_extra, c.escolaridade, 
            c.cep, c.pcd, c.tem_ctps, -- Incluindo os novos campos
            e.funcao_id, e.anos_experiencia, e.meses_experiencia
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

    def update_curriculo(self, curriculo_id, nome, cpf, sexo, data_nascimento, cidade_id, telefone, telefone_extra, escolaridade, tem_ctps, cep, pcd):
        """
        Atualiza os dados de um currículo com o novo campo PCD.
        """
        # Validações e limpeza de dados
        cpf = self.limpar_formatacao_cpf(cpf)
        telefone = self.limpar_formatacao_telefone(telefone)
        telefone_extra = self.limpar_formatacao_telefone(telefone_extra) if telefone_extra else None
        
        if not self.validar_cpf(cpf):
            raise ValueError("CPF inválido. 11 dígitos requeridos.")
        
        if cep:
            cep = re.sub(r"\D", "", cep)
            if len(cep) != 8:
                raise ValueError("CEP deve conter 8 dígitos.")

        # Query atualizada com campo PCD
        query = """
        UPDATE curriculo
        SET 
            nome = %s,
            cpf = %s,
            sexo = %s,
            data_nascimento = %s,
            cidade_id = %s,
            telefone = %s,
            telefone_extra = %s,
            escolaridade = %s,
            tem_ctps = %s,
            cep = %s,
            pcd = %s  -- Novo campo
        WHERE id = %s;
        """
        
        try:
            self.db.execute_query(
                query,
                (
                    nome, cpf, sexo, data_nascimento, cidade_id,
                    telefone, telefone_extra, escolaridade,
                    tem_ctps, cep, pcd,  # Novo valor PCD
                    curriculo_id
                )
            )
        except Exception as e:
            print(f"Erro SQL: {e}")
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

    def insert_curriculo(self, nome, cpf, sexo, data_nascimento, cidade_id, telefone, telefone_extra, escolaridade, tem_ctps, experiencias, cep, pcd):
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
        INSERT INTO curriculo (nome, cpf, sexo, data_nascimento, cidade_id, telefone, telefone_extra, escolaridade, tem_ctps, cep, pcd)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        try:
            curriculo_id = self.db.execute_query(
                query_curriculo,
                (nome, cpf, sexo, data_nascimento, cidade_id, telefone, telefone_extra, escolaridade, tem_ctps, cep, pcd),
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
        SELECT experiencias.funcao_id, anos_experiencia, meses_experiencia
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
        # Escolaridades padrão
        escolaridades_padrao = [
            "ENSINO FUNDAMENTAL INCOMPLETO",
            "ENSINO FUNDAMENTAL COMPLETO",
            "ENSINO MÉDIO INCOMPLETO",
            "ENSINO MÉDIO COMPLETO",
            "ENSINO SUPERIOR INCOMPLETO",
            "ENSINO SUPERIOR COMPLETO",
            "PÓS-GRADUAÇÃO/MBA",
            "MESTRADO",
            "DOUTORADO"
        ]
        
        # Inicializando o dicionário de distribuição com todas as escolaridades padrão e contagem 0
        distribucao_escolaridade = {escolaridade: 0 for escolaridade in escolaridades_padrao}

        # Consultando as escolaridades no banco
        query = """
        SELECT escolaridade, COUNT(id) AS total
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
        
        query += " GROUP BY escolaridade ORDER BY total DESC;"

        try:
            results = self.db.execute_query(query, fetch_all=True)
            # Preenchendo as escolaridades no dicionário
            for row in results:
                escolaridade = row['escolaridade']
                total = row['total']
                if escolaridade in distribucao_escolaridade:
                    distribucao_escolaridade[escolaridade] = total
            
            # Verificando o resultado
            print(f"Distribuição de Escolaridade com valores padrão: {distribucao_escolaridade}")
            return distribucao_escolaridade
        except Exception as e:
            print(f"Erro ao obter distribuição de escolaridade: {e}")
            return distribucao_escolaridade  # Retorna o dicionário com as escolaridades padrão

    def get_top_funcoes(self, filtro=None, limit=5):
        """
        Retorna as funções mais populares com base na contagem de currículos.
        """
        query = """
        SELECT f.nome AS funcao, COUNT(e.id_curriculo) AS total
        FROM experiencias e
        JOIN funcoes f ON e.funcao_id = f.id
        """

        # Aplicar filtro de data
        filtros = {
            "Últimos 30 dias": " JOIN curriculo c ON e.id_curriculo = c.id WHERE c.data_cadastro >= NOW() - INTERVAL '30 days'",
            "Últimos 6 meses": " JOIN curriculo c ON e.id_curriculo = c.id WHERE c.data_cadastro >= NOW() - INTERVAL '6 months'",
            "Último ano": " JOIN curriculo c ON e.id_curriculo = c.id WHERE c.data_cadastro >= NOW() - INTERVAL '1 year'"
        }
        
        if filtro in filtros:
            query += filtros[filtro]
        
        query += " GROUP BY f.nome ORDER BY total DESC LIMIT %s;"

        try:
            results = self.db.execute_query(query, (limit,), fetch_all=True)
            return {row['funcao']: row['total'] for row in results}
        except Exception as e:
            print(f"Erro ao obter top funções: {e}")
            return {}

    def get_ctps_distribuicao(self, filtro=None):
        """
        Retorna a distribuição entre currículos com CTPS e sem CTPS, aplicando filtros se necessário.
        """
        query = """
        SELECT 
            CASE 
                WHEN tem_ctps THEN 'Com CTPS'
                ELSE 'Sem CTPS'
            END AS categoria,
            COUNT(*) AS total
        FROM curriculo
        """
        
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
            print(f"Erro ao obter distribuição de CTPS: {e}")
            return {}

    def get_experiencia_media_por_idade(self, filtro=None):
        """
        Retorna a média de experiência TOTAL (anos + meses) por idade.
        """
        query = """
        SELECT
            FLOOR(DATE_PART('year', AGE(c.data_nascimento)) AS idade,
            AVG(e.anos_experiencia + (e.meses_experiencia/12.0)) AS experiencia_media
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
            return {row['idade']: float(row['experiencia_media']) for row in results}
        except Exception as e:
            print(f"Erro ao obter experiência média por idade: {e}")
            return {}
    
    def get_faixa_etaria_distribuicao(self, filtro=None):
        """
        Retorna a distribuição de candidatos por faixa etária corrigida.
        """
        query = """
        SELECT
            CASE
                WHEN idade BETWEEN 18 AND 24 THEN '18-24'
                WHEN idade BETWEEN 25 AND 34 THEN '25-34'
                WHEN idade BETWEEN 35 AND 44 THEN '35-44'
                WHEN idade BETWEEN 45 AND 54 THEN '45-54'
                ELSE '55+'
            END AS faixa_etaria,
            COUNT(*) AS total
        FROM (
            SELECT FLOOR(DATE_PART('year', AGE(data_nascimento)) AS idade
            FROM curriculo
        ) AS idades
        """

        # Aplicar filtro de data
        filtros = {
            "Últimos 30 dias": " WHERE data_cadastro >= NOW() - INTERVAL '30 days'",
            "Últimos 6 meses": " WHERE data_cadastro >= NOW() - INTERVAL '6 months'",
            "Último ano": " WHERE data_cadastro >= NOW() - INTERVAL '1 year'"
        }
        
        if filtro in filtros:
            query = query.replace("FROM curriculo", f"FROM curriculo {filtros[filtro]}")
        
        query += " GROUP BY faixa_etaria ORDER BY faixa_etaria;"
        
        try:
            results = self.db.execute_query(query, fetch_all=True)
            return {row['faixa_etaria']: row['total'] for row in results}
        except Exception as e:
            print(f"Erro ao obter distribuição de faixa etária: {e}")
            return {}

    def delete_curriculo(self, curriculo_id):
        """
        Deleta um currículo pelo ID.
        """
        query = "DELETE FROM curriculo WHERE id = %s;"
        try:
            self.db.execute_query(query, (curriculo_id,))
        except Exception as e:
            print(f"Erro ao deletar currículo: {e}")
            raise