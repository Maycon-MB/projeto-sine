import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout,
    QWidget, QPushButton, QMessageBox, QComboBox, QLabel, QHeaderView, QLineEdit, QCheckBox
)
from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import Qt


class TelaNotificacoes(QDialog):
    def __init__(self, aprovacao_model, usuario_id, tipo_usuario):
        super().__init__()
        self.model = aprovacao_model  
        self.usuario_id = usuario_id
        self.tipo_usuario = tipo_usuario
        self.setWindowTitle("Notificações")
        self.setMinimumSize(900, 700)

        # Variáveis de paginação
        self.page = 1
        self.page_size = 10
        self.total_pages = 1

        # Layout principal
        self.layout = QVBoxLayout()

        # Barra de busca e filtro
        filtro_layout = QHBoxLayout()
        self.busca_input = QLineEdit()
        self.busca_input.setPlaceholderText("Buscar notificações...")
        self.busca_input.textChanged.connect(self.carregar_notificacoes)

        filtro_label = QLabel("Filtrar por status:")
        self.filtro_combo = QComboBox()
        self.filtro_combo.addItems(["Todos", "pendente", "aprovado", "rejeitado"])
        self.filtro_combo.currentIndexChanged.connect(self.carregar_notificacoes)

        filtro_layout.addWidget(self.busca_input)
        filtro_layout.addWidget(filtro_label)
        filtro_layout.addWidget(self.filtro_combo)
        self.layout.addLayout(filtro_layout)

        # Tabela de notificações
        self.tabela_notificacoes = QTableWidget()
        self.tabela_notificacoes.setColumnCount(7)
        self.tabela_notificacoes.setHorizontalHeaderLabels(
            ["Selecionar", "Usuário", "Email", "Cidade", "Data de Cadastro", "Status", "Ações"]
        )
        self.tabela_notificacoes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.tabela_notificacoes)

        # Botões de paginação e ações em massa
        botoes_layout = QHBoxLayout()
        self.btn_anterior = QPushButton("Anterior")
        self.btn_anterior.clicked.connect(self.pagina_anterior)

        self.page_label = QLabel(f"Página: {self.page}/{self.total_pages}")

        self.btn_proxima = QPushButton("Próxima")
        self.btn_proxima.clicked.connect(self.pagina_proxima)

        self.btn_mass_aprovar = QPushButton("Aprovar Selecionados")
        self.btn_mass_aprovar.clicked.connect(self.aprovar_selecionados)

        self.btn_mass_rejeitar = QPushButton("Rejeitar Selecionados")
        self.btn_mass_rejeitar.clicked.connect(self.rejeitar_selecionados)

        botoes_layout.addWidget(self.btn_anterior)
        botoes_layout.addWidget(self.page_label)
        botoes_layout.addWidget(self.btn_proxima)
        botoes_layout.addStretch()
        botoes_layout.addWidget(self.btn_mass_aprovar)
        botoes_layout.addWidget(self.btn_mass_rejeitar)

        self.layout.addLayout(botoes_layout)
        self.setLayout(self.layout)

        # Carregar notificações
        self.carregar_notificacoes()

        self.tabela_notificacoes.setColumnWidth(6, 200)  # Define largura mínima para a coluna "Ações"

    def carregar_notificacoes(self):
        """
        Carrega as notificações com base no filtro, busca e paginação.
        """
        try:
            filtro_status = self.filtro_combo.currentText()
            busca = self.busca_input.text()
            if filtro_status == "Todos":
                filtro_status = None

            notificacoes, total_notificacoes = self.model.listar_aprovacoes_paginadas(
                usuario_id=self.usuario_id,
                tipo_usuario=self.tipo_usuario,
                status=filtro_status,
                busca=busca,
                page=self.page,
                page_size=self.page_size
            )

            self.total_pages = max(1, (total_notificacoes + self.page_size - 1) // self.page_size)
            self.tabela_notificacoes.setRowCount(len(notificacoes))

            for row, notificacao in enumerate(notificacoes):
                checkbox = QTableWidgetItem()
                checkbox.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox.setCheckState(Qt.Unchecked)
                self.tabela_notificacoes.setItem(row, 0, checkbox)

                self.tabela_notificacoes.setItem(row, 1, self._criar_celula(notificacao["usuario"]))
                self.tabela_notificacoes.item(row, 1).setData(Qt.UserRole, notificacao["id"])
                self.tabela_notificacoes.setItem(row, 2, self._criar_celula(notificacao["email"]))
                self.tabela_notificacoes.setItem(row, 3, self._criar_celula(notificacao["cidade"]))
                self.tabela_notificacoes.setItem(row, 4, self._criar_celula(notificacao["criado_em"]))

                status_item = self._criar_celula(notificacao["status_aprovacao"])
                if notificacao["status_aprovacao"] == "pendente":
                    # Define um amarelo mais suave
                    status_item.setBackground(QColor("#f28b24"))  # LemonChiffon, por exemplo
                elif notificacao["status_aprovacao"] == "aprovado":
                    # Define um verde com tom personalizado
                    status_item.setBackground(QColor("#02b002"))  # LightGreen
                elif notificacao["status_aprovacao"] == "rejeitado":
                    # Define um vermelho com tom personalizado
                    status_item.setBackground(QColor("#c20000"))  # Um tom de vermelho claro
                self.tabela_notificacoes.setItem(row, 5, status_item)

                btn_aprovar = QPushButton("✔")
                btn_aprovar.setToolTip("Aprovar")
                btn_aprovar.setEnabled(notificacao["status_aprovacao"] == "pendente")
                btn_aprovar.clicked.connect(lambda _, id=notificacao["id"]: self.aprovar(id))

                btn_rejeitar = QPushButton("✖")
                btn_rejeitar.setToolTip("Rejeitar")
                btn_rejeitar.setEnabled(notificacao["status_aprovacao"] == "pendente")
                btn_rejeitar.clicked.connect(lambda _, id=notificacao["id"]: self.rejeitar(id))

                self.tabela_notificacoes.setCellWidget(row, 6, self._criar_widget_acoes(btn_aprovar, btn_rejeitar))

            self.page_label.setText(f"Página: {self.page}/{self.total_pages}")
        except Exception as e:
            logging.error(f"Erro ao carregar notificações: {str(e)}")

    def _criar_celula(self, texto):
        item = QTableWidgetItem(str(texto))
        item.setTextAlignment(Qt.AlignCenter)
        item.setToolTip(str(texto))
        return item

    def _criar_widget_acoes(self, *botoes):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remover margens
        layout.setSpacing(2)  # Reduzir espaçamento entre botões
        for btn in botoes:
            layout.addWidget(btn)
        layout.setAlignment(Qt.AlignCenter)
        widget.setLayout(layout)
        return widget

    def aprovar(self, aprovacao_id):
        """
        Exibe um diálogo para selecionar o tipo de usuário antes de aprovar.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Aprovar Usuário")
        layout = QVBoxLayout()

        label = QLabel("Selecione o nível do usuário:")
        tipo_combo = QComboBox()
        tipo_combo.addItems(["master", "admin", "comum"])

        btn_confirmar = QPushButton("Confirmar")
        btn_confirmar.clicked.connect(lambda: self._confirmar_aprovacao(dialog, aprovacao_id, tipo_combo.currentText()))

        layout.addWidget(label)
        layout.addWidget(tipo_combo)
        layout.addWidget(btn_confirmar)
        dialog.setLayout(layout)
        dialog.exec()

    def _confirmar_aprovacao(self, dialog, aprovacao_id, tipo_usuario_novo):
        """
        Confirma a aprovação e define o nível do usuário.
        """
        try:
            self.model.aprovar_usuario(aprovacao_id, self.usuario_id, self.tipo_usuario, tipo_usuario_novo)
            QMessageBox.information(self, "Sucesso", f"Usuário aprovado como {tipo_usuario_novo}!")
            self.carregar_notificacoes()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao aprovar: {str(e)}")
        finally:
            dialog.accept()

    def rejeitar(self, aprovacao_id):
        """
        Rejeita a solicitação de usuário.
        """
        try:
            self.model.rejeitar_usuario(aprovacao_id, self.usuario_id, self.tipo_usuario)
            QMessageBox.information(self, "Sucesso", "Solicitação rejeitada!")
            self.carregar_notificacoes()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao rejeitar: {str(e)}")

    def aprovar_selecionados(self):
        self._aplicar_acao_em_selecionados("aprovado")

    def rejeitar_selecionados(self):
        self._aplicar_acao_em_selecionados("rejeitado")

    def _aplicar_acao_em_selecionados(self, status):
        ids_selecionados = []
        for row in range(self.tabela_notificacoes.rowCount()):
            checkbox = self.tabela_notificacoes.item(row, 0)
            if checkbox and checkbox.checkState() == Qt.Checked:
                notificacao_id = self.tabela_notificacoes.item(row, 1).data(Qt.UserRole)  # ID armazenado no UserRole
                ids_selecionados.append(notificacao_id)

        if not ids_selecionados:
            QMessageBox.warning(self, "Aviso", "Nenhuma notificação selecionada.")
            return

        try:
            for notificacao_id in ids_selecionados:
                self.model.atualizar_status_aprovacao(
                    notificacao_id, status, usuario_id=self.usuario_id, tipo_usuario=self.tipo_usuario
                )
            QMessageBox.information(self, "Sucesso", f"Notificações {status}s com sucesso!")
            self.carregar_notificacoes()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao aplicar ação: {str(e)}")

    def pagina_anterior(self):
        if self.page > 1:
            self.page -= 1
            self.carregar_notificacoes()

    def pagina_proxima(self):
        if self.page < self.total_pages:
            self.page += 1
            self.carregar_notificacoes()
