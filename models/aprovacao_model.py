from database.connection import DatabaseConnection
import logging

class AprovacaoModel:
    def __init__(self, db_connection):
        self.db = db_connection
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def enviar_aprovacao(self, usuario_id, cidade):
        query = """
        INSERT INTO aprovacoes (usuario_id, cidade)
        VALUES (%s, %s);
        """
        self.db.execute_query(query, (usuario_id, cidade))
        logging.info(f"Aprovação registrada para o usuário ID: {usuario_id}")

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
        offset = (page - 1) * page_size
        query = """
        SELECT 
            a.id, u.usuario, u.email, u.cidade, a.criado_em, a.status_aprovacao
        FROM 
            aprovacoes a
        INNER JOIN 
            usuarios u ON a.usuario_id = u.id
        WHERE 
            (%s IS NULL OR a.status_aprovacao = %s)
        ORDER BY 
            a.criado_em DESC
        LIMIT %s OFFSET %s;
        """
        return self.db.execute_query(query, (status, status, page_size, offset), fetch_all=True)

    def atualizar_status_aprovacao(self, aprovacao_id, novo_status, usuario_id):
        """
        Atualiza o status de uma aprovação e registra a ação no log de auditoria.
        """
        if novo_status not in ['aprovado', 'rejeitado']:
            raise ValueError("Status inválido. Use 'aprovado' ou 'rejeitado'.")

        try:
            # Atualiza o status de aprovação
            query = """
                UPDATE aprovacoes
                SET status_aprovacao = %s, atualizado_em = NOW()
                WHERE id = %s;
            """
            self.db.execute_query(query, (novo_status, aprovacao_id))

            # Registra a ação no logs_auditoria
            log_query = """
                INSERT INTO logs_auditoria (notificacao_id, usuario_id, acao)
                VALUES (%s, %s, %s);
            """
            self.db.execute_query(log_query, (aprovacao_id, usuario_id, novo_status))
            logging.info(f"Aprovação ID: {aprovacao_id} atualizada para '{novo_status}' por usuário ID: {usuario_id}.")
        except Exception as e:
            logging.error(f"Erro ao atualizar status de aprovação: {e}")
            raise RuntimeError("Erro ao atualizar status de aprovação.") from e

    def aprovar_usuario(self, aprovacao_id, usuario_id):
        """
        Aprova uma solicitação e registra no log de auditoria.
        """
        self.atualizar_status_aprovacao(aprovacao_id, 'aprovado', usuario_id)

    def rejeitar_usuario(self, aprovacao_id, usuario_id):
        """
        Rejeita uma solicitação e registra no log de auditoria.
        """
        self.atualizar_status_aprovacao(aprovacao_id, 'rejeitado', usuario_id)

    def obter_aprovacao_por_id(self, aprovacao_id):
        query = """
            SELECT usuario_id
            FROM aprovacoes
            WHERE id = %s;
        """
        result = self.db.execute_query(query, (aprovacao_id,), fetch_one=True)
        return result  # Retorna o usuário associado à aprovação

    def total_pendentes(self):
        """Conta o total de aprovações pendentes."""
        query = "SELECT COUNT(*) FROM aprovacoes WHERE status_aprovacao = 'pendente';"
        result = self.db.execute_query(query, fetch_one=True)
        return result['count'] if result else 0

    def total_notificacoes(self):
        """Conta o total de notificações não lidas."""
        query = "SELECT COUNT(*) FROM notificacoes WHERE lido = FALSE;"
        result = self.db.execute_query(query, fetch_one=True)
        return result['count'] if result else 0
