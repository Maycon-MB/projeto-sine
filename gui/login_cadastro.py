from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QTabWidget,
    QWidget, QFormLayout, QHBoxLayout, QInputDialog
)
from PySide6.QtCore import Qt
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

    def criar_tab_login(self):
        tab_login = QWidget()
        layout = QVBoxLayout()

        self.login_usuario_input = QLineEdit()
        self.login_usuario_input.setPlaceholderText("Usuário ou E-mail")

        self.login_senha_input = self.criar_password_field("Senha")

        btn_login = QPushButton("Login")
        btn_login.clicked.connect(self.handle_login)

        btn_recuperar_senha = QPushButton("Esqueceu a senha?")
        btn_recuperar_senha.setFlat(True)
        btn_recuperar_senha.clicked.connect(self.handle_reset_password)

        layout.addWidget(QLabel("Usuário ou E-mail:"))
        layout.addWidget(self.login_usuario_input)
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(self.login_senha_input)
        layout.addWidget(btn_login)
        layout.addWidget(btn_recuperar_senha, alignment=Qt.AlignRight)

        tab_login.setLayout(layout)
        return tab_login

    def criar_tab_cadastro(self):
        tab_cadastro = QWidget()
        layout = QFormLayout()

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome completo")

        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Usuário")

        self.cidade_input = QLineEdit()
        self.cidade_input.setPlaceholderText("Cidade")

        self.cadastro_email_input = QLineEdit()
        self.cadastro_email_input.setPlaceholderText("E-mail")

        self.cadastro_password_input = self.criar_password_field("Senha")
        self.confirm_password_input = self.criar_password_field("Confirme a senha")

        btn_cadastrar = QPushButton("Cadastrar")
        btn_cadastrar.clicked.connect(self.handle_cadastro)

        layout.addRow("Nome:", self.nome_input)
        layout.addRow("Usuário:", self.usuario_input)
        layout.addRow("Cidade:", self.cidade_input)
        layout.addRow("E-mail:", self.cadastro_email_input)
        layout.addRow("Senha:", self.cadastro_password_input)
        layout.addRow("Confirme a Senha:", self.confirm_password_input)
        layout.addRow(btn_cadastrar)

        tab_cadastro.setLayout(layout)
        return tab_cadastro

    def criar_password_field(self, placeholder):
        container = QWidget()
        layout = QHBoxLayout()

        password_input = QLineEdit()
        password_input.setPlaceholderText(placeholder)
        password_input.setEchoMode(QLineEdit.Password)

        btn_toggle = QPushButton("👁")
        btn_toggle.setCheckable(True)
        btn_toggle.setMaximumWidth(30)

        def toggle_password():
            if btn_toggle.isChecked():
                password_input.setEchoMode(QLineEdit.Normal)
                btn_toggle.setText("🙈")
            else:
                password_input.setEchoMode(QLineEdit.Password)
                btn_toggle.setText("👁")

        btn_toggle.clicked.connect(toggle_password)
        layout.addWidget(password_input)
        layout.addWidget(btn_toggle)
        container.setLayout(layout)
        return container

    def is_valid_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

    def handle_login(self):
        usuario = self.login_usuario_input.text().strip()
        senha = self.login_senha_input.findChild(QLineEdit).text()

        if not usuario or not senha:
            QMessageBox.warning(self, "Erro", "Por favor, preencha todos os campos.")
            return

        try:
            usuario_info = self.usuario_model.buscar_usuario_por_login(usuario)
            if usuario_info and bcrypt.checkpw(senha.encode(), usuario_info['senha'].encode()):
                QMessageBox.information(self, "Sucesso", "Login realizado com sucesso!")
                self.usuario_logado = usuario_info  # ✅ Armazena o usuário logado
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao realizar login: {e}")


    def handle_cadastro(self):
        nome = self.nome_input.text().strip()
        usuario = self.usuario_input.text().strip()
        cidade = self.cidade_input.text().strip()
        email = self.cadastro_email_input.text().strip()
        senha = self.cadastro_password_input.findChild(QLineEdit).text()
        confirmacao = self.confirm_password_input.findChild(QLineEdit).text()

        if not nome or not usuario or not cidade or not email or not senha:
            QMessageBox.warning(self, "Erro", "Todos os campos devem ser preenchidos.")
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
            # Verificar duplicidade antes de cadastrar
            if self.usuario_model.verificar_email_existente(email):
                QMessageBox.warning(self, "Erro", "E-mail já cadastrado.")
                return

            if self.usuario_model.verificar_usuario_existente(usuario):
                QMessageBox.warning(self, "Erro", "Usuário já cadastrado.")
                return

            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.usuario_model.cadastrar_usuario(usuario, senha_hash, email, cidade, "comum")
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
