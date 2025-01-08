from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QWidget, QPushButton, QMessageBox
)


class TelaNotificacoes(QDialog):  # Alterado para QDialog
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setWindowTitle("Notificações")
        self.setMinimumSize(400, 300)

        # Layout principal
        self.layout = QVBoxLayout()

        # Tabela de notificações
        self.tabela_notificacoes = QTableWidget()
        self.tabela_notificacoes.setColumnCount(3)
        self.tabela_notificacoes.setHorizontalHeaderLabels(["Usuário", "Email", "Ações"])
        self.layout.addWidget(self.tabela_notificacoes)

        self.carregar_notificacoes()

        self.setLayout(self.layout)

    def carregar_notificacoes(self):
        """
        Carrega as notificações na tabela.
        """
        try:
            notificacoes = self.model.listar_aprovacoes_pendentes()
            self.tabela_notificacoes.setRowCount(len(notificacoes))

            for row, notificacao in enumerate(notificacoes):
                usuario_item = QTableWidgetItem(notificacao["usuario"])
                email_item = QTableWidgetItem(notificacao["email"])

                # Botão de Aprovar
                btn_aprovar = QPushButton("Aprovar")
                btn_aprovar.clicked.connect(lambda _, id=notificacao["id"]: self.aprovar(id))

                # Botão de Rejeitar
                btn_rejeitar = QPushButton("Rejeitar")
                btn_rejeitar.clicked.connect(lambda _, id=notificacao["id"]: self.rejeitar(id))

                self.tabela_notificacoes.setItem(row, 0, usuario_item)
                self.tabela_notificacoes.setItem(row, 1, email_item)
                self.tabela_notificacoes.setCellWidget(row, 2, self._criar_widget_acoes(btn_aprovar, btn_rejeitar))
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
        Aprova a solicitação com confirmação.
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
        Rejeita a solicitação com confirmação.
        """
        resposta = QMessageBox.question(self, "Confirmação", "Tem certeza que deseja rejeitar esta solicitação?")
        if resposta == QMessageBox.Yes:
            try:
                self.model.atualizar_status_aprovacao(aprovacao_id, "rejeitado")
                QMessageBox.information(self, "Sucesso", "Rejeição concluída!")
                self.carregar_notificacoes()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao rejeitar: {str(e)}")
