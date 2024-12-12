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
