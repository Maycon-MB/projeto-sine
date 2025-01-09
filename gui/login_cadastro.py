from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QInputDialog
)
from database.models import UsuarioModel
import hashlib


class LoginCadastroDialog(QDialog):
    def __init__(self, usuario_model):
        super().__init__()
        self.usuario_model = usuario_model
        self.setWindowTitle("Login e Cadastro")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)

        # Tabs
        self.tab_widget = QTabWidget(self)
        layout.addWidget(self.tab_widget)

        # Telas de Login e Cadastro
        self.login_tab = QWidget()
        self.cadastro_tab = QWidget()
        self.tab_widget.addTab(self.login_tab, "Login")
        self.tab_widget.addTab(self.cadastro_tab, "Cadastro")

        self.setup_login_tab()
        self.setup_cadastro_tab()

    def setup_login_tab(self):
        layout = QVBoxLayout(self.login_tab)

        form = QFormLayout()
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Digite seu usuário ou e-mail")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Digite sua senha")
        self.password_input.setEchoMode(QLineEdit.Password)
        form.addRow("Usuário/E-mail:", self.login_input)
        form.addRow("Senha:", self.password_input)

        layout.addLayout(form)

        # Botões
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.reset_button = QPushButton("Esqueci Minha Senha")
        self.reset_button.clicked.connect(self.handle_reset_password)
        layout.addWidget(self.reset_button)

    def setup_cadastro_tab(self):
        layout = QVBoxLayout(self.cadastro_tab)

        form = QFormLayout()
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Digite seu nome completo")
        self.cadastro_email_input = QLineEdit()
        self.cadastro_email_input.setPlaceholderText("Digite seu e-mail")
        self.cadastro_password_input = QLineEdit()
        self.cadastro_password_input.setPlaceholderText("Digite sua senha")
        self.cadastro_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirme sua senha")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        form.addRow("Nome:", self.nome_input)
        form.addRow("E-mail:", self.cadastro_email_input)
        form.addRow("Senha:", self.cadastro_password_input)
        form.addRow("Confirmar Senha:", self.confirm_password_input)

        layout.addLayout(form)

        # Botões
        self.cadastro_button = QPushButton("Cadastrar")
        self.cadastro_button.clicked.connect(self.handle_cadastro)
        layout.addWidget(self.cadastro_button)

    def handle_login(self):
        """Valida login."""
        usuario = self.login_input.text().strip()
        senha = hashlib.sha256(self.password_input.text().encode()).hexdigest()
        try:
            user = self.usuario_model.validar_login(usuario, senha)
            if user:
                QMessageBox.information(self, "Bem-vindo", f"Login bem-sucedido, {user['usuario']}!")
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao realizar login: {e}")

    def handle_cadastro(self):
        """Realiza o cadastro de um novo usuário e envia solicitação de autorização."""
        nome = self.nome_input.text().strip()
        email = self.cadastro_email_input.text().strip()
        senha = self.cadastro_password_input.text()
        confirmacao = self.confirm_password_input.text()

        if not nome or not email or not senha:
            QMessageBox.warning(self, "Erro", "Todos os campos devem ser preenchidos.")
            return

        if senha != confirmacao:
            QMessageBox.warning(self, "Erro", "As senhas não conferem.")
            return

        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        try:
            user_id = self.usuario_model.cadastrar_usuario(nome, senha_hash, email, "comum")
            QMessageBox.information(self, "Cadastro", "Cadastro realizado com sucesso! Aguarde aprovação.")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao realizar cadastro: {e}")

    def handle_reset_password(self):
        """Abre a lógica de recuperação de senha."""
        email, ok = QInputDialog.getText(self, "Recuperação de Senha", "Digite seu e-mail:")
        if ok and email:
            try:
                token = self.usuario_model.gerar_token_recuperacao(email)
                QMessageBox.information(self, "Recuperação de Senha", f"Token de recuperação enviado para {email}.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao enviar token: {e}")
