from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QTabWidget, QComboBox,
    QWidget, QFormLayout, QHBoxLayout, QInputDialog
)
from PySide6.QtCore import Qt, QEvent
import re
import bcrypt


class LoginCadastroDialog(QDialog):
    def __init__(self, usuario_model, parent=None):
        super().__init__(parent)
        self.usuario_model = usuario_model
        self.setWindowTitle("Login e Cadastro")
        self.setMinimumSize(400, 300)

        self.layout_principal = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.criar_tab_login(), "Login")
        self.tabs.addTab(self.criar_tab_cadastro(), "Cadastro")
        self.layout_principal.addWidget(self.tabs)

        self.setLayout(self.layout_principal)
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #c2dafc; /* Azul acinzentado claro */
            }
            QLabel {
                font-size: 14px;
                color: #333333; /* Texto em cinza escuro */
            }
            QLineEdit, QComboBox {
                background-color: #ffffff; /* Fundo branco */
                border: 1px solid #b0c4de; /* Azul desaturado */
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                color: #333333; /* Texto em cinza escuro */
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #0078d7; /* Azul profissional no foco */
            }
            QPushButton {
                background-color: #0078d7; /* Azul principal */
                color: #ffffff; /* Texto branco */
                font-size: 14px;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #005499; /* Azul mais escuro no hover */
            }
            QPushButton:disabled {
                background-color: #c0c0c0; /* Cinza claro para desabilitado */
                color: #808080; /* Texto em cinza médio */
            }
            QTabWidget::pane {
                border: 1px solid #b0c4de; /* Azul desaturado */
            }
            QTabBar::tab {
                background: #f4f6f9; /* Fundo claro para abas inativas */
                color: #0078d7; /* Texto em azul profissional */
                padding: 8px;
                border: 1px solid #b0c4de;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #0078d7; /* Fundo azul para aba ativa */
                color: #ffffff; /* Texto branco */
            }
            QTabBar::tab:hover {
                background: #005499; /* Fundo mais escuro no hover */
            }
        """)

    def criar_tab_login(self):
        tab_login = QWidget()
        layout = QVBoxLayout()

        self.login_usuario_input = QLineEdit()
        self.login_usuario_input.setPlaceholderText("Usuário ou E-mail")
        self.login_usuario_input.editingFinished.connect(
            lambda: self.login_usuario_input.setText(self.login_usuario_input.text().upper())
        )

        self.login_senha_input, password_container = self.criar_password_field("Senha")

        btn_login = QPushButton("Login")
        btn_login.setObjectName("Login")  # Nome único para identificação
        btn_login.clicked.connect(self.handle_login)

        btn_recuperar_senha = QPushButton("Esqueceu a senha?")
        btn_recuperar_senha.setFlat(True)
        btn_recuperar_senha.clicked.connect(self.handle_reset_password)

        layout.addWidget(QLabel("Usuário ou E-mail:"))
        layout.addWidget(self.login_usuario_input)
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(password_container)  # Substituído pelo container horizontal
        layout.addWidget(btn_login)
        layout.addWidget(btn_recuperar_senha, alignment=Qt.AlignRight)

        self.configurar_transicao_enter([
            self.login_usuario_input,
            self.login_senha_input,
            btn_login,
        ])

        tab_login.setLayout(layout)
        return tab_login

    def criar_tab_cadastro(self):
        tab_cadastro = QWidget()
        layout = QFormLayout()

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome completo")
        self.nome_input.editingFinished.connect(lambda: self.nome_input.setText(self.nome_input.text().upper()))

        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Usuário")
        self.usuario_input.editingFinished.connect(lambda: self.usuario_input.setText(self.usuario_input.text().upper()))

        self.cidade_combobox = QComboBox()
        self.cidade_combobox.setEditable(True)  # Permitir digitação
        self.preencher_combo_cidades()

        self.cadastro_email_input = QLineEdit()
        self.cadastro_email_input.setPlaceholderText("E-mail")

        self.cadastro_password_input, password_container = self.criar_password_field("Senha")
        self.confirm_password_input, confirm_password_container = self.criar_password_field("Confirme a senha")

        btn_cadastrar = QPushButton("Cadastrar")
        btn_cadastrar.setObjectName("Cadastrar")  # Nome único para identificação
        btn_cadastrar.clicked.connect(self.handle_cadastro)

        layout.addRow("Nome:", self.nome_input)
        layout.addRow("Usuário:", self.usuario_input)
        layout.addRow("Cidade:", self.cidade_combobox)
        layout.addRow("E-mail:", self.cadastro_email_input)
        layout.addRow("Senha:", password_container)  # Substituído pelo container horizontal
        layout.addRow("Confirme a Senha:", confirm_password_container)  # Substituído pelo container horizontal
        layout.addRow(btn_cadastrar)

        self.configurar_transicao_enter([
            self.nome_input,
            self.usuario_input,
            self.cidade_combobox,
            self.cadastro_email_input,
            self.cadastro_password_input,
            self.confirm_password_input,
        ])

        tab_cadastro.setLayout(layout)
        return tab_cadastro

    def preencher_combo_cidades(self):
        """
        Preenche o ComboBox com as cidades da tabela 'cidades'.
        """
        try:
            cidades = self.usuario_model.listar_cidades()  # Nova função no modelo
            self.cidade_combobox.addItem("")  # Placeholder inicial
            for cidade in cidades:
                self.cidade_combobox.addItem(cidade['nome'], cidade['id'])  # Adiciona com nome e ID
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar cidades: {e}")

    def criar_password_field(self, placeholder):
        """Cria um campo de senha com botão de mostrar/ocultar."""
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margens extras

        password_input = QLineEdit()
        password_input.setPlaceholderText(placeholder)
        password_input.setEchoMode(QLineEdit.Password)

        btn_toggle = QPushButton("👁")
        btn_toggle.setCheckable(True)
        btn_toggle.setMaximumWidth(30)

        # Alternar visibilidade da senha
        def toggle_password():
            if btn_toggle.isChecked():
                password_input.setEchoMode(QLineEdit.Normal)
                btn_toggle.setText("🙈")
            else:
                password_input.setEchoMode(QLineEdit.Password)
                btn_toggle.setText("👁")

        btn_toggle.clicked.connect(toggle_password)

        # Adicionar o campo e o botão ao layout horizontal
        layout.addWidget(password_input)
        layout.addWidget(btn_toggle)
        container.setLayout(layout)
        return password_input, container

    def configurar_transicao_enter(self, widgets):
        """Configura a navegação entre widgets usando Enter."""
        for i, widget in enumerate(widgets):
            widget.setProperty("index", i)  # Define o índice do widget
            widget.installEventFilter(self)  # Instala o filtro de eventos

    def eventFilter(self, source, event):
        """Captura o evento Enter para alternar entre widgets e acionar o botão."""
        if event.type() == QEvent.KeyPress and event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Lista de widgets para o cadastro
            widgets_cadastro = [
                self.nome_input,
                self.usuario_input,
                self.cidade_combobox,
                self.cadastro_email_input,
                self.cadastro_password_input,
                self.confirm_password_input,
            ]

            # Lista de widgets para o login
            widgets_login = [
                self.login_usuario_input,
                self.login_senha_input,
            ]

            # Verifica a navegação na aba de cadastro
            if source in widgets_cadastro:
                current_index = widgets_cadastro.index(source)
                next_index = current_index + 1
                if next_index < len(widgets_cadastro):
                    widgets_cadastro[next_index].setFocus()
                else:
                    self.findChild(QPushButton, "Cadastrar").click()
                return True  # Evento tratado

            # Verifica a navegação na aba de login
            if source in widgets_login:
                current_index = widgets_login.index(source)
                next_index = current_index + 1
                if next_index < len(widgets_login):
                    widgets_login[next_index].setFocus()
                else:
                    self.findChild(QPushButton, "Login").click()
                return True  # Evento tratado
        return super().eventFilter(source, event)
    
    def configurar_transicao_enter(self, widgets):
        """Configura a navegação entre widgets usando Enter."""
        for widget in widgets:
            widget.installEventFilter(self)

    def is_valid_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

    def handle_login(self):
        usuario = self.login_usuario_input.text().strip()
        senha = self.login_senha_input.text()

        if not usuario or not senha:
            QMessageBox.warning(self, "Erro", "Por favor, preencha todos os campos.")
            return

        try:
            # Busca as informações do usuário pelo login (usuário ou email)
            usuario_info = self.usuario_model.buscar_usuario_por_login(usuario)

            if usuario_info and bcrypt.checkpw(senha.encode(), usuario_info['senha'].encode()):
                QMessageBox.information(self, "Sucesso", "Login realizado com sucesso!")

                # Adiciona 'tipo_usuario' ao dicionário de usuário logado
                self.usuario_logado = {
                    'id': usuario_info['id'],
                    'usuario': usuario_info['usuario'],
                    'email': usuario_info['email'],
                    'cidade_id': usuario_info['cidade_id'],
                    'tipo_usuario': usuario_info['tipo_usuario'],  # Certifique-se de que este campo está no banco
                }

                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao realizar login: {e}")

    def handle_cadastro(self):
        nome = self.nome_input.text().strip()
        usuario = self.usuario_input.text().strip()
        cidade_id = self.cidade_combobox.currentData()  # Recupera o ID da cidade selecionada
        email = self.cadastro_email_input.text().strip()
        senha = self.cadastro_password_input.text()
        confirmacao = self.confirm_password_input.text()

        if not nome or not usuario or not cidade_id or not email or not senha:
            QMessageBox.warning(self, "Erro", "Todos os campos devem ser preenchidos.")
            return

        if cidade_id is None or cidade_id == "Selecione uma cidade":
            QMessageBox.warning(self, "Erro", "Por favor, selecione uma cidade válida.")
            return

        if not self.is_valid_email(email):
            QMessageBox.warning(self, "Erro", "E-mail inválido.")
            return

        if senha != confirmacao:
            QMessageBox.warning(self, "Erro", "As senhas não conferem.")
            return

        if not re.match(r"^[a-zA-Z0-9_]+$", usuario):
            QMessageBox.warning(self, "Erro", "O nome de usuário contém caracteres inválidos.")
            return

        try:
            if self.usuario_model.verificar_email_existente(email):
                QMessageBox.warning(self, "Erro", "E-mail já cadastrado.")
                return

            if self.usuario_model.verificar_usuario_existente(usuario):
                QMessageBox.warning(self, "Erro", "Usuário já cadastrado.")
                return

            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.usuario_model.cadastrar_usuario(usuario, senha_hash, email, cidade_id, "comum")  # Passa cidade_id
            QMessageBox.information(self, "Cadastro", "Cadastro realizado com sucesso!")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao realizar cadastro: {e}")

    def handle_reset_password(self):
        email, ok = QInputDialog.getText(self, "Recuperação de Senha", "Digite seu e-mail:")
        if ok and email:
            if not self.is_valid_email(email):
                QMessageBox.warning(self, "Erro", "E-mail inválido.")
                return

            try:
                if not self.usuario_model.verificar_email_existente(email):
                    QMessageBox.warning(self, "Erro", "E-mail não cadastrado.")
                    return

                self.usuario_model.enviar_token_recuperacao(email)
                QMessageBox.information(self, "Recuperação de Senha", f"Token enviado para {email}. Verifique seu e-mail.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao enviar token: {e}")

    def showEvent(self, event):
        """Coloca o foco no campo de Login quando a janela for exibida."""
        self.login_usuario_input.setFocus()  # Foca no campo "Usuário ou E-mail"
        super().showEvent(event)  # Chama o evento showEvent da classe base
