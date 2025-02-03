
import logging


class NotificacaoModel:
    def __init__(self, db_connection):
        self.db = db_connection
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    def enviar_aprovacao(self, usuario_id, cidade):
        """
        Registra uma nova aprovação no sistema.
        """
        query = """
        INSERT INTO aprovacoes (usuario_id, cidade)
        VALUES (%s, %s);
        """
        self.db.execute_query(query, (usuario_id, cidade))

    def listar_aprovacoes_pendentes(self, usuario_id, tipo_usuario, cidade_admin=None):
        """
        Lista aprovações pendentes com restrições baseadas no tipo de usuário.
        """
        query = """
        SELECT a.id, u.usuario, u.email, ci.nome AS cidade, a.criado_em, a.status_aprovacao
        FROM aprovacoes a
        INNER JOIN usuarios u ON a.usuario_id = u.id
        INNER JOIN cidades ci ON u.cidade_id = ci.id
        WHERE a.status_aprovacao = 'pendente'
        """
        params = []

        if tipo_usuario == "admin":
            query += " AND ci.nome = %s"
            params.append(cidade_admin)
        elif tipo_usuario == "comum":
            raise PermissionError("Usuários comuns não têm acesso às aprovações.")

        query += " ORDER BY a.criado_em ASC;"
        return self.db.execute_query(query, params, fetch_all=True)

    def listar_aprovacoes_paginadas(
        self, usuario_id, tipo_usuario, status=None, page=1, page_size=10, cidade_admin=None, busca=None
    ):
        """
        Lista aprovações paginadas com base em filtros e suporte a busca.
        Retorna uma lista vazia e total de notificações igual a zero quando não há dados.
        """
        try:
            # Calcular o offset para paginação
            offset = (page - 1) * page_size

            # Base da consulta
            base_query = """
            SELECT 
                a.id, 
                u.usuario, 
                u.email, 
                ci.nome AS cidade, 
                a.criado_em, 
                a.status_aprovacao
            FROM 
                aprovacoes a
            INNER JOIN 
                usuarios u ON a.usuario_id = u.id
            INNER JOIN 
                cidades ci ON u.cidade_id = ci.id
            WHERE 
                1 = 1
            """
            params = []

            # Adicionar filtro por status, se aplicável
            if status:
                base_query += " AND a.status_aprovacao = %s"
                params.append(status)

            # Adicionar filtro de busca, se aplicável
            if busca:
                base_query += " AND (u.usuario ILIKE %s OR u.email ILIKE %s OR ci.nome ILIKE %s)"
                busca_param = f"%{busca}%"
                params.extend([busca_param, busca_param, busca_param])

            # Restrições por tipo de usuário
            if tipo_usuario == "admin":
                if not cidade_admin:
                    raise ValueError("cidade_admin deve ser fornecida para usuários do tipo 'admin'.")
                base_query += " AND ci.nome = %s"
                params.append(cidade_admin)
            elif tipo_usuario == "comum":
                raise PermissionError("Usuários comuns não têm acesso às aprovações.")

            # Consulta para obter o total de notificações
            count_query = f"SELECT COUNT(*) FROM ({base_query}) AS subquery;"
            count_params = params[:]

            # Consulta paginada
            paginated_query = base_query + " ORDER BY a.criado_em DESC LIMIT %s OFFSET %s;"
            params.extend([page_size, offset])

            # Executar consulta de contagem
            total_notificacoes = self.db.execute_query(count_query, count_params, fetch_one=True)

            # Validar o retorno da contagem
            if total_notificacoes and "count" in total_notificacoes:
                total_notificacoes = total_notificacoes["count"]
            else:
                logging.warning("Consulta de contagem retornou None ou formato inesperado. Definindo total_notificacoes como 0.")
                total_notificacoes = 0

            # Executar consulta paginada
            notificacoes = self.db.execute_query(paginated_query, params, fetch_all=True)

            if notificacoes is None:
                raise ValueError("Consulta paginada retornou None.")

            # Converta cada linha para um dicionário normal
            notificacoes = [dict(row) for row in notificacoes]

            # Validar estrutura das notificações
            for notificacao in notificacoes:
                required_keys = {"id", "usuario", "email", "cidade", "criado_em", "status_aprovacao"}
                if not required_keys.issubset(notificacao.keys()):
                    raise KeyError(f"Faltando chaves esperadas na notificação: {notificacao}")

            return notificacoes, total_notificacoes

        except Exception as e:
            # Log de erro detalhado
            logging.error(f"Erro em listar_aprovacoes_paginadas: {str(e)}")
            raise

    def atualizar_status_aprovacao(self, aprovacao_id, novo_status, usuario_id, tipo_usuario):
        """
        Atualiza o status de uma aprovação e registra no log de auditoria.
        """
        if tipo_usuario == "comum":
            raise PermissionError("Usuários comuns não podem alterar aprovações.")

        if novo_status not in ["aprovado", "rejeitado"]:
            raise ValueError("Status inválido. Use 'aprovado' ou 'rejeitado'.")

        try:
            query = """
                UPDATE aprovacoes
                SET status_aprovacao = %s, atualizado_em = NOW()
                WHERE id = %s;
            """
            self.db.execute_query(query, (novo_status, aprovacao_id))

            log_query = """
                INSERT INTO logs_auditoria (notificacao_id, usuario_id, acao)
                VALUES (%s, %s, %s);
            """
            self.db.execute_query(log_query, (aprovacao_id, usuario_id, novo_status))
        except Exception as e:
            logging.error(f"Erro ao atualizar status de aprovação: {e}")
            raise RuntimeError("Erro ao atualizar status de aprovação.") from e

    def aprovar_usuario(self, aprovacao_id, usuario_id, tipo_usuario, tipo_usuario_novo):
        """
        Aprova um usuário e define seu nível (master, admin ou comum).
        """
        logging.info(f"Aprovando usuário com ID {aprovacao_id}, alterando tipo para '{tipo_usuario_novo}'")
        if tipo_usuario == "comum":
            raise PermissionError("Usuários comuns não podem aprovar outros usuários.")

        if tipo_usuario_novo not in ["master", "admin", "comum"]:
            raise ValueError("Tipo de usuário inválido. Escolha entre 'master', 'admin' ou 'comum'.")

        try:
            # Atualiza o status da aprovação
            self.atualizar_status_aprovacao(aprovacao_id, "aprovado", usuario_id, tipo_usuario)

            # Obtém o usuário associado à aprovação
            usuario_aprovado = self.obter_aprovacao_por_id(aprovacao_id)
            if not usuario_aprovado:
                raise ValueError("Usuário não encontrado para aprovação.")

            usuario_id_aprovado = usuario_aprovado["usuario_id"]

            # Atualiza o nível do usuário aprovado
            query = """
                UPDATE usuarios
                SET tipo_usuario = %s
                WHERE id = %s;
            """
            self.db.execute_query(query, (tipo_usuario_novo, usuario_id_aprovado))

            # Criar notificação para o usuário aprovado
            descricao = f"Seu cadastro foi aprovado! Você agora tem acesso como {tipo_usuario_novo}."
            self.criar_notificacao(usuario_id_aprovado, "Aprovação de Cadastro", descricao)

        except Exception as e:
            logging.error(f"Erro ao aprovar usuário: {e}")
            raise RuntimeError("Erro ao aprovar usuário.") from e

    def rejeitar_usuario(self, aprovacao_id, usuario_id, tipo_usuario):
        """
        Rejeita um usuário e o notifica.
        """
        if tipo_usuario == "comum":
            raise PermissionError("Usuários comuns não podem rejeitar aprovações.")

        try:
            self.atualizar_status_aprovacao(aprovacao_id, "rejeitado", usuario_id, tipo_usuario)

            # Obter o usuário rejeitado
            usuario_rejeitado = self.obter_aprovacao_por_id(aprovacao_id)
            if not usuario_rejeitado:
                raise ValueError("Usuário não encontrado para rejeição.")

            usuario_id_rejeitado = usuario_rejeitado["usuario_id"]

            # Criar notificação para o usuário rejeitado
            descricao = "Seu cadastro foi rejeitado. Caso tenha dúvidas, entre em contato com o suporte."
            self.criar_notificacao(usuario_id_rejeitado, "Rejeição de Cadastro", descricao)

        except Exception as e:
            logging.error(f"Erro ao rejeitar usuário: {e}")
            raise RuntimeError("Erro ao rejeitar usuário.") from e

    def obter_aprovacao_por_id(self, aprovacao_id):
        query = """
            SELECT usuario_id
            FROM aprovacoes
            WHERE id = %s;
        """
        result = self.db.execute_query(query, (aprovacao_id,), fetch_one=True)
        return result
    
    def criar_notificacao(self, usuario_id, evento, descricao):
        """
        Registra uma nova notificação para o usuário.
        """
        try:
            query = """
            INSERT INTO notificacoes (usuario_id, evento, descricao, criado_em, lido)
            VALUES (%s, %s, %s, NOW(), FALSE);
            """
            self.db.execute_query(query, (usuario_id, evento, descricao))
        except Exception as e:
            logging.error(f"Erro ao registrar notificação: {str(e)}")

    def total_pendentes(self, tipo_usuario, cidade_admin=None):
        query = "SELECT COUNT(*) FROM aprovacoes WHERE status_aprovacao = 'pendente'"
        params = []

        if tipo_usuario == "admin":
            query += " AND cidade = %s"
            params.append(cidade_admin)
        elif tipo_usuario == "comum":
            raise PermissionError("Usuários comuns não têm acesso às aprovações.")

        result = self.db.execute_query(query, params, fetch_one=True)
        return result["count"] if result else 0

    def total_notificacoes(self, usuario_id):
        query = "SELECT COUNT(*) FROM notificacoes WHERE usuario_id = %s AND lido = FALSE;"
        result = self.db.execute_query(query, (usuario_id,), fetch_one=True)
        return result["count"] if result else 0