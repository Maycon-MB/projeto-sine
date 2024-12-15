from database.connection import DatabaseConnection

class CurriculoModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def is_duplicate(self, nome, telefone):
        query = """
            SELECT COUNT(*) FROM curriculos WHERE nome = %s OR telefone = %s
        """
        result = self.db.execute_query(query, (nome, telefone), fetch_one=True)
        return result['count'] > 0

    def insert_curriculo(self, nome, idade, telefone, escolaridade, experiencias):
        query = """
            INSERT INTO curriculos (nome, idade, telefone, escolaridade, experiencias)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.db.execute_query(query, (nome, idade, telefone, escolaridade, experiencias))

    def fetch_curriculo(self, curriculo_id):
        query = """
            SELECT * FROM curriculos WHERE id = %s
        """
        return self.db.execute_query(query, (curriculo_id,), fetch_one=True)

    def fetch_all_curriculos(self, nome=None, escolaridade=None, idade_min=None, idade_max=None):
        query = "SELECT * FROM curriculos WHERE 1=1"
        params = []

        if nome:
            query += " AND nome ILIKE %s"
            params.append(f"%{nome}%")
        if escolaridade:
            query += " AND escolaridade = %s"
            params.append(escolaridade)
        if idade_min:
            query += " AND idade >= %s"
            params.append(idade_min)
        if idade_max:
            query += " AND idade <= %s"
            params.append(idade_max)

        return self.db.execute_query(query, tuple(params), fetch_all=True)
