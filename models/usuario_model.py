from database.connection import DatabaseConnection
from email_utils import enviar_email
from models.notificacao_model import NotificacaoModel
import bcrypt
import logging


class UsuarioModel:
    def __init__(self, db_connection):
        self.db = db_connection
        self.notificacao_model = NotificacaoModel(db_connection)  # Integração com NotificacaoModel
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def verificar_email_existente(self, email):
        query = "SELECT 1 FROM usuarios WHERE email = %s"
        result = self.db.execute_query(query, (email.upper(),), fetch_one=True)
        return result is not None

    def verificar_usuario_existente(self, usuario):
        query = "SELECT 1 FROM usuarios WHERE usuario = %s"
        result = self.db.execute_query(query, (usuario.upper(),), fetch_one=True)
        return result is not None
    
    def buscar_cidade_id(self, cidade_nome):
        query = "SELECT id FROM cidades WHERE nome = %s"
        result = self.db.execute_query(query, (cidade_nome.upper(),), fetch_one=True)
        if result:
            return result['id']
        raise ValueError(f"Cidade '{cidade_nome}' não encontrada.")

    def cadastrar_usuario(self, usuario, senha, email, cidade_id, tipo_usuario):
        try:
            usuario = usuario.upper()
            email = email.upper()

            if self.verificar_email_existente(email):
                raise ValueError("E-mail já cadastrado.")
            if self.verificar_usuario_existente(usuario):
                raise ValueError("Usuário já cadastrado.")

            # Gerando o hash da senha
            senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()  # Retorna uma string

            query = """
            INSERT INTO usuarios (usuario, senha, email, cidade_id, tipo_usuario)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """
            result = self.db.execute_query(query, (usuario, senha_hash, email, cidade_id, tipo_usuario), fetch_one=True)

            # Envia aprovação pendente para o admin/master
            self.notificacao_model.enviar_aprovacao(result['id'], cidade_id)
            logging.info(f"Usuário cadastrado com ID: {result['id']}, aguardando aprovação.")
            return result['id']
        except Exception as e:
            logging.error(f"Erro ao cadastrar usuário: {e}")
            raise

    def listar_cidades(self):
        """
        Retorna uma lista de cidades disponíveis no banco de dados.
        """
        query = "SELECT id, nome FROM cidades ORDER BY nome;"
        return self.db.execute_query(query, fetch_all=True)


    def _registrar_log(self, usuario_id, acao):
        query = "INSERT INTO logs_auditoria (usuario_id, acao) VALUES (%s, %s);"
        self.db.execute_query(query, (usuario_id, acao))

    def gerar_token_recuperacao(self, email):
        import uuid
        token = str(uuid.uuid4())
        try:
            query = """
            INSERT INTO recuperacao_senha (usuario_id, token, expiracao)
            VALUES ((SELECT id FROM usuarios WHERE email = %s), %s, CURRENT_TIMESTAMP + INTERVAL '1 day')
            RETURNING token;
            """
            result = self.db.execute_query(query, (email.upper(), token), fetch_one=True)
            mensagem = f"Use o seguinte token para redefinir sua senha: {token}"
            enviar_email(email, "Recuperação de Senha", mensagem)
            self._registrar_log(result['token'], 'Token de recuperação gerado')
            return result['token']
        except Exception as e:
            logging.error(f"Erro ao gerar token de recuperação: {e}")
            raise

    def redefinir_senha(self, token, nova_senha):
        senha_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()
        try:
            query = """
            UPDATE usuarios
            SET senha = %s
            WHERE id = (
                SELECT usuario_id FROM recuperacao_senha
                WHERE token = %s AND expiracao > CURRENT_TIMESTAMP AND usado = FALSE
            );
            """
            self.db.execute_query(query, (senha_hash, token))
            self.db.execute_query("UPDATE recuperacao_senha SET usado = TRUE WHERE token = %s;", (token,))
            self._registrar_log(None, 'Senha redefinida com token')
        except Exception as e:
            logging.error(f"Erro ao redefinir senha: {e}")
            raise

    def validar_login(self, usuario, senha):
        query = "SELECT id, senha FROM usuarios WHERE UPPER(usuario) = %s OR UPPER(email) = %s"
        result = self.db.execute_query(query, (usuario.upper(), usuario.upper()), fetch_one=True)

        if not result:
            logging.warning("Usuário ou e-mail não encontrado.")
            return False

        senha_hash_armazenada = result['senha']

        # Converter senha armazenada para bytes se estiver como string
        if isinstance(senha_hash_armazenada, str):
            senha_hash_armazenada = senha_hash_armazenada.encode()

        if bcrypt.checkpw(senha.encode(), senha_hash_armazenada):
            logging.info(f"Usuário {usuario} autenticado com sucesso.")
            return True

        logging.warning("Senha incorreta.")
        return False

    def buscar_usuario_por_login(self, usuario):
        query = """
        SELECT id, usuario, email, cidade_id, tipo_usuario, senha
        FROM usuarios
        WHERE usuario = %s OR email = %s
        """
        result = self.db.execute_query(query, (usuario.upper(), usuario.upper()), fetch_one=True)
        
        if result:
            logging.info(f"Usuário encontrado: {result['usuario']}, Senha Hash: {result['senha']}")
        
        return result
    
    def total_curriculos(self):
        """Conta o total de currículos cadastrados."""
        query = "SELECT COUNT(*) FROM curriculo;"
        result = self.db.execute_query(query, fetch_one=True)
        return result['count'] if result else 0

    def cidades_com_curriculos(self):
        """
        Retorna uma lista com o número de currículos agrupados por cidade.
        """
        query = """
        SELECT ci.nome, COUNT(c.id) AS total
        FROM curriculo c
        INNER JOIN cidades ci ON c.cidade_id = ci.id
        GROUP BY ci.nome
        ORDER BY total DESC;
        """
        return self.db.execute_query(query, fetch_all=True)
