from database.connection import DatabaseConnection
from email_utils import enviar_email
import bcrypt

class UsuarioModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def verificar_email_existente(self, email):
        query = "SELECT 1 FROM usuarios WHERE email = %s"
        result = self.db.execute_query(query, (email,), fetch_one=True)
        return result is not None

    def verificar_usuario_existente(self, usuario):
        query = "SELECT 1 FROM usuarios WHERE usuario = %s"
        result = self.db.execute_query(query, (usuario,), fetch_one=True)
        return result is not None


    def cadastrar_usuario(self, usuario, senha, email, cidade, tipo_usuario):
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
        self._enviar_aprovacao(result['id'], cidade)
        return result['id']

    def _enviar_aprovacao(self, usuario_id, cidade):
        query = """
        INSERT INTO aprovacoes (usuario_id, cidade)
        VALUES (%s, %s);
        """
        self.db.execute_query(query, (usuario_id, cidade))

    def listar_aprovacoes_pendentes(self, cidade_admin=None, usuario_id=None):
        query = """
        SELECT a.id, u.usuario, u.email, a.criado_em
        FROM aprovacoes a
        INNER JOIN usuarios u ON a.usuario_id = u.id
        WHERE a.status_aprovacao = 'pendente'
        """
        params = []

        if usuario_id:
            query += " AND u.id = %s"
            params.append(usuario_id)
        elif cidade_admin:
            query += " AND a.cidade = %s"
            params.append(cidade_admin)

        query += " ORDER BY a.criado_em ASC;"
        
        return self.db.execute_query(query, params, fetch_all=True)


    def listar_aprovacoes_paginadas(self, status=None, page=1, page_size=10):
        query = """
        SELECT a.id, u.usuario, u.email, u.cidade, a.criado_em
        FROM aprovacoes a
        INNER JOIN usuarios u ON a.usuario_id = u.id
        WHERE (%s IS NULL OR a.status_aprovacao = %s)
        ORDER BY a.criado_em DESC
        LIMIT %s OFFSET %s;
        """
        offset = (page - 1) * page_size
        try:
            return self.db.execute_query(query, (status, status, page_size, offset), fetch_all=True)
        except Exception as e:
            raise RuntimeError(f"Erro ao listar aprovações paginadas: {e}")

    def atualizar_status_aprovacao(self, aprovacao_id, novo_status, usuario_id):
        query = """
            UPDATE aprovacoes
            SET status_aprovacao = %s, atualizado_em = NOW()
            WHERE id = %s;
        """
        log_query = """
            INSERT INTO logs_auditoria (notificacao_id, usuario_id, acao)
            VALUES (%s, %s, %s);
        """
        self.db.execute_query(query, (novo_status, aprovacao_id))
        self.db.execute_query(log_query, (aprovacao_id, usuario_id, novo_status))

    def aprovar_usuario(self, aprovacao_id):
        query = """
        UPDATE aprovacoes
        SET status_aprovacao = 'aprovado', atualizado_em = CURRENT_TIMESTAMP
        WHERE id = %s;
        """
        self.db.execute_query(query, (aprovacao_id,))

    def rejeitar_usuario(self, aprovacao_id):
        query = """
        UPDATE aprovacoes
        SET status_aprovacao = 'rejeitado', atualizado_em = CURRENT_TIMESTAMP
        WHERE id = %s;
        """
        self.db.execute_query(query, (aprovacao_id,))

    def gerar_token_recuperacao(self, email):
        import uuid
        token = str(uuid.uuid4())  # Gera um token único
        query = """
        INSERT INTO recuperacao_senha (usuario_id, token, expiracao)
        VALUES (
            (SELECT id FROM usuarios WHERE email = %s), %s, CURRENT_TIMESTAMP + INTERVAL '1 day'
        )
        RETURNING token;
        """
        try:
            result = self.db.execute_query(query, (email, token), fetch_one=True)
            mensagem = f"""
            Você solicitou a recuperação de sua senha. Use o seguinte token para redefinir sua senha:
            
            {token}
            
            Este token é válido por 24 horas.
            
            Caso você não tenha solicitado, ignore este e-mail.
            """
            enviar_email(email, "Recuperação de Senha", mensagem)
            return result['token']
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar token de recuperação: {e}")

    def redefinir_senha(self, token, nova_senha_hash):
        query = """
        UPDATE usuarios
        SET senha = %s
        WHERE id = (
            SELECT usuario_id FROM recuperacao_senha
            WHERE token = %s AND expiracao > CURRENT_TIMESTAMP AND usado = FALSE
        );
        """
        try:
            self.db.execute_query(query, (nova_senha_hash, token))
            self.db.execute_query("UPDATE recuperacao_senha SET usado = TRUE WHERE token = %s;", (token,))
        except Exception as e:
            raise RuntimeError(f"Erro ao redefinir senha: {e}")

    def validar_login(self, usuario, senha):
        query = "SELECT senha FROM usuarios WHERE usuario = %s OR email = %s"
        try:
            result = self.db.execute_query(query, (usuario, usuario), fetch_one=True)
            if result:
                if bcrypt.checkpw(senha.encode(), result['senha'].encode()):
                    return True
            return False
        except Exception as e:
            raise RuntimeError(f"Erro ao validar login: {e}")

    def buscar_usuario_por_login(self, usuario):
        query = "SELECT id, senha FROM usuarios WHERE usuario = %s OR email = %s"
        try:
            return self.db.execute_query(query, (usuario, usuario), fetch_one=True)
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            raise
