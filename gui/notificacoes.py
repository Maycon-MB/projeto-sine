from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QWidget, QPushButton, QMessageBox, QComboBox, QLabel
)


class TelaNotificacoes(QDialog):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setWindowTitle("Notificações")
        self.setMinimumSize(500, 400)

        # Variáveis de paginação
        self.page = 1
        self.page_size = 10

        # Layout principal
        self.layout = QVBoxLayout()

        # Filtro de status
        filtro_layout = QHBoxLayout()
        filtro_label = QLabel("Filtrar por status:")
        self.filtro_combo = QComboBox()
        self.filtro_combo.addItems(["Todos", "pendente", "aprovado", "rejeitado"])
        self.filtro_combo.currentIndexChanged.connect(self.carregar_notificacoes)

        filtro_layout.addWidget(filtro_label)
        filtro_layout.addWidget(self.filtro_combo)
        self.layout.addLayout(filtro_layout)

        # Tabela de notificações
        self.tabela_notificacoes = QTableWidget()
        self.tabela_notificacoes.setColumnCount(5)
        self.tabela_notificacoes.setHorizontalHeaderLabels(["Usuário", "Email", "Cidade", "Data de Cadastro", "Ações"])
        self.layout.addWidget(self.tabela_notificacoes)

        # Botões de paginação e atualização
        botoes_layout = QHBoxLayout()
        self.btn_anterior = QPushButton("Anterior")
        self.btn_anterior.clicked.connect(self.pagina_anterior)
        self.btn_anterior.setEnabled(False)  # Desativado inicialmente

        self.btn_proxima = QPushButton("Próxima")
        self.btn_proxima.clicked.connect(self.pagina_proxima)

        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.clicked.connect(self.carregar_notificacoes)

        botoes_layout.addWidget(self.btn_anterior)
        botoes_layout.addWidget(self.btn_proxima)
        botoes_layout.addWidget(self.btn_atualizar)
        self.layout.addLayout(botoes_layout)

        self.setLayout(self.layout)

        # Carregar notificações
        self.carregar_notificacoes()

    def carregar_notificacoes(self):
        """
        Carrega as notificações na tabela com base no filtro e paginação.
        """
        try:
            filtro_status = self.filtro_combo.currentText()
            if filtro_status == "Todos":
                filtro_status = None

            notificacoes = self.model.listar_aprovacoes_paginadas(
                status=filtro_status, page=self.page, page_size=self.page_size
            )

            self.tabela_notificacoes.setRowCount(len(notificacoes))

            for row, notificacao in enumerate(notificacoes):
                usuario_item = QTableWidgetItem(notificacao["usuario"])
                email_item = QTableWidgetItem(notificacao["email"])
                cidade_item = QTableWidgetItem(notificacao["cidade"])
                data_item = QTableWidgetItem(notificacao["criado_em"])

                # Botão de Aprovar
                btn_aprovar = QPushButton("Aprovar")
                btn_aprovar.clicked.connect(lambda _, id=notificacao["id"]: self.aprovar(id))

                # Botão de Rejeitar
                btn_rejeitar = QPushButton("Rejeitar")
                btn_rejeitar.clicked.connect(lambda _, id=notificacao["id"]: self.rejeitar(id))

                self.tabela_notificacoes.setItem(row, 0, usuario_item)
                self.tabela_notificacoes.setItem(row, 1, email_item)
                self.tabela_notificacoes.setItem(row, 2, cidade_item)
                self.tabela_notificacoes.setItem(row, 3, data_item)
                self.tabela_notificacoes.setCellWidget(row, 4, self._criar_widget_acoes(btn_aprovar, btn_rejeitar))

            # Atualizar estado dos botões de paginação
            self.btn_anterior.setEnabled(self.page > 1)
            self.btn_proxima.setEnabled(len(notificacoes) == self.page_size)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar notificações: {str(e)}")

    def _criar_widget_acoes(self, btn_aprovar, btn_rejeitar):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(btn_aprovar)
        layout.addWidget(btn_rejeitar)
        widget.setLayout(layout)
        return widget

    def aprovar(self, aprovacao_id):
        """
        Aprova a solicitação com confirmação e registra log.
        """
        resposta = QMessageBox.question(self, "Confirmação", "Tem certeza que deseja aprovar esta solicitação?")
        if resposta == QMessageBox.Yes:
            try:
                self.model.atualizar_status_aprovacao(aprovacao_id, "aprovado")
                QMessageBox.information(self, "Sucesso", "Aprovação concluída!")
                self.carregar_notificacoes()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao aprovar: {str(e)}")

    def rejeitar(self, aprovacao_id):
        """
        Rejeita a solicitação com confirmação e registra log.
        """
        resposta = QMessageBox.question(self, "Confirmação", "Tem certeza que deseja rejeitar esta solicitação?")
        if resposta == QMessageBox.Yes:
            try:
                self.model.atualizar_status_aprovacao(aprovacao_id, "rejeitado")
                QMessageBox.information(self, "Sucesso", "Rejeição concluída!")
                self.carregar_notificacoes()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao rejeitar: {str(e)}")

    def pagina_anterior(self):
        if self.page > 1:
            self.page -= 1
            self.carregar_notificacoes()

    def pagina_proxima(self):
        self.page += 1
        self.carregar_notificacoes()
