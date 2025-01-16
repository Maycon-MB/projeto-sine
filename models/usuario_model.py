from database.connection import DatabaseConnection
from email_utils import enviar_email
from models.aprovacao_model import AprovacaoModel
import bcrypt
import logging


class UsuarioModel:
    def __init__(self, db_connection):
        self.db = db_connection
        self.aprovacao_model = AprovacaoModel(db_connection)  # Integração com AprovacaoModel
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def verificar_email_existente(self, email):
        query = "SELECT 1 FROM usuarios WHERE email = %s"
        result = self.db.execute_query(query, (email.upper(),), fetch_one=True)
        return result is not None

    def verificar_usuario_existente(self, usuario):
        query = "SELECT 1 FROM usuarios WHERE usuario = %s"
        result = self.db.execute_query(query, (usuario.upper(),), fetch_one=True)
        return result is not None

    def cadastrar_usuario(self, usuario, senha, email, cidade, tipo_usuario):
        try:
            usuario = usuario.upper()
            email = email.upper()
            cidade = cidade.upper()

            if self.verificar_email_existente(email):
                raise ValueError("E-mail já cadastrado.")
            if self.verificar_usuario_existente(usuario):
                raise ValueError("Usuário já cadastrado.")

            senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
            query = """
            INSERT INTO usuarios (usuario, senha, email, cidade, tipo_usuario)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """
            result = self.db.execute_query(query, (usuario, senha_hash, email, cidade, tipo_usuario), fetch_one=True)
            self.aprovacao_model.enviar_aprovacao(result['id'], cidade)  # Usa AprovacaoModel
            self._registrar_log(result['id'], 'Cadastro de usuário')
            return result['id']
        except Exception as e:
            logging.error(f"Erro ao cadastrar usuário: {e}")
            raise

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
        query = "SELECT senha FROM usuarios WHERE usuario = %s OR email = %s"
        result = self.db.execute_query(query, (usuario.upper(), usuario.upper()), fetch_one=True)
        if result and bcrypt.checkpw(senha.encode(), result['senha'].encode()):
            return True
        return False

    def buscar_usuario_por_login(self, usuario):
        query = "SELECT id, senha FROM usuarios WHERE usuario = %s OR email = %s"
        return self.db.execute_query(query, (usuario.upper(), usuario.upper()), fetch_one=True)
    
    def total_curriculos(self):
        """Conta o total de currículos cadastrados."""
        query = "SELECT COUNT(*) FROM curriculo;"
        result = self.db.execute_query(query, fetch_one=True)
        return result['count'] if result else 0

