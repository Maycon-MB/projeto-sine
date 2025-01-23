from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout,
    QWidget, QPushButton, QMessageBox, QComboBox, QLabel, QHeaderView
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt


class TelaNotificacoes(QDialog):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setWindowTitle("Notificações")
        self.setMinimumSize(800, 600)

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
        self.tabela_notificacoes.setColumnCount(6)
        self.tabela_notificacoes.setHorizontalHeaderLabels(
            ["Usuário", "Email", "Cidade", "Data de Cadastro", "Status", "Ações"]
        )
        self.tabela_notificacoes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.tabela_notificacoes)

        # Botões de paginação e atualização
        botoes_layout = QHBoxLayout()
        self.btn_anterior = QPushButton("Anterior")
        self.btn_anterior.clicked.connect(self.pagina_anterior)
        self.btn_anterior.setEnabled(False)

        self.btn_proxima = QPushButton("Próxima")
        self.btn_proxima.clicked.connect(self.pagina_proxima)

        self.btn_atualizar = QPushButton()
        self.btn_atualizar.setIcon(QIcon("assets/icons/refresh-icon.svg"))
        self.btn_atualizar.setToolTip("Atualizar")
        self.btn_atualizar.clicked.connect(self.carregar_notificacoes)

        self.page_label = QLabel(f"Página: {self.page}")
        botoes_layout.addWidget(self.btn_anterior)
        botoes_layout.addWidget(self.page_label)
        botoes_layout.addWidget(self.btn_proxima)
        botoes_layout.addStretch()
        botoes_layout.addWidget(self.btn_atualizar)

        self.layout.addLayout(botoes_layout)
        self.setLayout(self.layout)

        # Carregar notificações
        self.carregar_notificacoes()

    def carregar_notificacoes(self):
        """
        Carrega as notificações com base no filtro e paginação.
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
                self.tabela_notificacoes.setItem(row, 0, self._criar_celula(notificacao["usuario"]))
                self.tabela_notificacoes.setItem(row, 1, self._criar_celula(notificacao["email"]))
                self.tabela_notificacoes.setItem(row, 2, self._criar_celula(notificacao["cidade"]))
                self.tabela_notificacoes.setItem(row, 3, self._criar_celula(notificacao["criado_em"]))
                self.tabela_notificacoes.setItem(row, 4, self._criar_celula(notificacao["status_aprovacao"]))

                # Botões de ação
                btn_aprovar = QPushButton("✔")
                btn_aprovar.setToolTip("Aprovar")
                btn_aprovar.setEnabled(notificacao["status_aprovacao"] == "pendente")
                btn_aprovar.clicked.connect(lambda _, id=notificacao["id"]: self.aprovar(id))

                btn_rejeitar = QPushButton("✖")
                btn_rejeitar.setToolTip("Rejeitar")
                btn_rejeitar.setEnabled(notificacao["status_aprovacao"] == "pendente")
                btn_rejeitar.clicked.connect(lambda _, id=notificacao["id"]: self.rejeitar(id))

                self.tabela_notificacoes.setCellWidget(row, 5, self._criar_widget_acoes(btn_aprovar, btn_rejeitar))

            self.page_label.setText(f"Página: {self.page}")
            self.btn_anterior.setEnabled(self.page > 1)
            self.btn_proxima.setEnabled(len(notificacoes) == self.page_size)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar notificações: {str(e)}")

    def _criar_celula(self, texto):
        item = QTableWidgetItem(str(texto))
        item.setTextAlignment(Qt.AlignCenter)
        item.setToolTip(str(texto))
        return item

    def _criar_widget_acoes(self, btn_aprovar, btn_rejeitar):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(btn_aprovar)
        layout.addWidget(btn_rejeitar)
        layout.setAlignment(Qt.AlignCenter)
        widget.setLayout(layout)
        return widget

    def aprovar(self, aprovacao_id):
        if QMessageBox.question(self, "Confirmação", "Aprovar esta solicitação?") == QMessageBox.Yes:
            try:
                # Obter o usuario_id relacionado à aprovacao_id
                usuario_id = self._obter_usuario_id(aprovacao_id)
                
                # Passar o usuario_id para o método atualizar_status_aprovacao
                self.model.atualizar_status_aprovacao(aprovacao_id, "aprovado", usuario_id)
                QMessageBox.information(self, "Sucesso", "Solicitação aprovada!")
                self.carregar_notificacoes()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao aprovar: {str(e)}")

    def rejeitar(self, aprovacao_id):
        if QMessageBox.question(self, "Confirmação", "Rejeitar esta solicitação?") == QMessageBox.Yes:
            try:
                # Obter o usuario_id relacionado à aprovacao_id
                usuario_id = self._obter_usuario_id(aprovacao_id)
                
                # Passar o usuario_id para o método atualizar_status_aprovacao
                self.model.atualizar_status_aprovacao(aprovacao_id, "rejeitado", usuario_id)
                QMessageBox.information(self, "Sucesso", "Solicitação rejeitada!")
                self.carregar_notificacoes()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao rejeitar: {str(e)}")

    def _obter_usuario_id(self, aprovacao_id):
        """
        Obtém o ID do usuário associado ao aprovacao_id.
        """
        # Aqui você pode usar o model para buscar o usuario_id relacionado à aprovação.
        aprovacao = self.model.obter_aprovacao_por_id(aprovacao_id)
        return aprovacao['usuario_id']  # Retorna o ID do usuário associado

    def pagina_anterior(self):
        if self.page > 1:
            self.page -= 1
            self.carregar_notificacoes()

    def pagina_proxima(self):
        self.page += 1
        self.carregar_notificacoes()
