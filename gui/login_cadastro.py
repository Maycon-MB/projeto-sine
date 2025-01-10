from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QFormLayout, QLineEdit, QPushButton, QLabel,
    QMessageBox, QInputDialog, QHBoxLayout
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from database.models import UsuarioModel
import hashlib


class LoginCadastroDialog(QDialog):
    def __init__(self, usuario_model):
        super().__init__()
        self.usuario_model = usuario_model
        self.setWindowTitle("Login e Cadastro")
        self.setMinimumSize(400, 400)

        # Estilo Azul aplicado em toda a tela e abas
        self.setStyleSheet("""
            QDialog {
                background-color: #191970;
            }
            QTabWidget::pane {
                background-color: #191970;
                border: 1px solid #191970;
            }
            QTabBar::tab {
                background-color: #191970;
                color: white;
                padding: 10px;
                font-weight: bold;
                min-width: 120px;  /* Mesma largura para abas */
            }
            QTabBar::tab:selected {
                background-color: #0056A1;
            }
            QLabel {
                font-size: 14px;
                color: white;
            }
            QLineEdit {
                background-color: white;
                padding: 8px;
                border-radius: 5px;
                font-size: 14px;
                color: black;
                min-height: 35px;
                min-width: 250px;  /* Tamanho fixo para todos os campos */
            }
            QPushButton {
                background-color: #4682B4;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #4169E1;
            }
            QLineEdit[echoMode="2"] {
                color: black;
            }
        """)


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
        layout.setAlignment(Qt.AlignTop)  # Alinha tudo ao topo

        # Login
        login_label = QLabel("Login")
        login_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-bottom: 2px;")
        layout.addWidget(login_label)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Digite seu usuário ou e-mail")
        layout.addWidget(self.login_input)

        # Senha com ícone de olho
        senha_label = QLabel("Senha")
        senha_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-top: 10px; margin-bottom: 2px;")
        layout.addWidget(senha_label)

        senha_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Digite sua senha")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.toggle_password_button = QPushButton()
        self.toggle_password_button.setIcon(QIcon("assets/icons/eye_closed.png"))
        self.toggle_password_button.setFixedSize(30, 30)
        self.toggle_password_button.setCheckable(True)
        self.toggle_password_button.setStyleSheet("background-color: transparent; border: none;")
        self.toggle_password_button.toggled.connect(
            lambda checked: self.toggle_password_visibility(checked, self.password_input, self.toggle_password_button)
        )

        senha_layout.addWidget(self.password_input)
        senha_layout.addWidget(self.toggle_password_button)
        layout.addLayout(senha_layout)

        # Botão de Login
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        # Botão de recuperação de senha
        self.reset_button = QPushButton("Esqueci Minha Senha")
        self.reset_button.clicked.connect(self.handle_reset_password)
        layout.addWidget(self.reset_button)


    def setup_cadastro_tab(self):
        layout = QVBoxLayout(self.cadastro_tab)
        layout.setAlignment(Qt.AlignTop)  # Alinha tudo ao topo

        # Nome
        nome_label = QLabel("Nome")
        nome_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-bottom: 2px;")
        layout.addWidget(nome_label)

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Digite seu nome")
        layout.addWidget(self.nome_input)

        # Usuário
        usuario_label = QLabel("Usuário")
        usuario_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-top: 10px; margin-bottom: 2px;")
        layout.addWidget(usuario_label)

        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Digite seu usuário")
        layout.addWidget(self.usuario_input)

        # Cidade
        cidade_label = QLabel("Cidade")
        cidade_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-top: 10px; margin-bottom: 2px;")
        layout.addWidget(cidade_label)

        self.cidade_input = QLineEdit()
        self.cidade_input.setPlaceholderText("Digite sua cidade")
        layout.addWidget(self.cidade_input)

        # E-mail
        email_label = QLabel("E-mail")
        email_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-top: 10px; margin-bottom: 2px;")
        layout.addWidget(email_label)

        self.cadastro_email_input = QLineEdit()
        self.cadastro_email_input.setPlaceholderText("Digite seu e-mail")
        layout.addWidget(self.cadastro_email_input)

        # Senha
        senha_label = QLabel("Senha")
        senha_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-top: 10px; margin-bottom: 2px;")
        layout.addWidget(senha_label)

        self.cadastro_password_input, self.toggle_cadastro_password_button = self.create_password_field()
        layout.addWidget(self.cadastro_password_input)

        # Confirmar Senha
        confirm_senha_label = QLabel("Confirmar Senha")
        confirm_senha_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-top: 10px; margin-bottom: 2px;")
        layout.addWidget(confirm_senha_label)

        self.confirm_password_input, self.toggle_confirm_password_button = self.create_password_field()
        layout.addWidget(self.confirm_password_input)

        # Botão de Cadastro
        self.cadastro_button = QPushButton("Cadastrar")
        self.cadastro_button.clicked.connect(self.handle_cadastro)
        layout.addWidget(self.cadastro_button)


    def create_password_field(self):
        """Cria um campo de senha com botão para exibir/ocultar com ícones."""
        password_layout = QHBoxLayout()
        password_input = QLineEdit()
        password_input.setPlaceholderText("Digite sua senha")
        password_input.setEchoMode(QLineEdit.Password)

        toggle_button = QPushButton()
        toggle_button.setIcon(QIcon("assets/icons/eye_closed.png"))  # Ícone de olho fechado
        toggle_button.setFixedSize(30, 30)
        toggle_button.setCheckable(True)
        toggle_button.setStyleSheet("background-color: transparent; border: none;")

        # Alternar visibilidade e ícone
        toggle_button.toggled.connect(lambda checked: self.toggle_password_visibility(checked, password_input, toggle_button))

        password_layout.addWidget(password_input)
        password_layout.addWidget(toggle_button)

        password_widget = QWidget()
        password_widget.setLayout(password_layout)

        return password_widget, toggle_button

    def toggle_password_visibility(self, checked, password_input, toggle_button):
        """Alterna a visibilidade da senha e o ícone."""
        if checked:
            password_input.setEchoMode(QLineEdit.Normal)
            toggle_button.setIcon(QIcon("assets/icons/eye_open.png"))  # Ícone de olho aberto
        else:
            password_input.setEchoMode(QLineEdit.Password)
            toggle_button.setIcon(QIcon("assets/icons/eye_closed.png"))  # Ícone de olho fechado

    def handle_login(self):
        """Valida login."""
        usuario = self.login_input.text().strip()
        senha = hashlib.sha256(self.password_input.findChild(QLineEdit).text().encode()).hexdigest()
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
        """Realiza o cadastro de um novo usuário."""
        nome = self.nome_input.text().strip()
        usuario = self.usuario_input.text().strip()
        cidade = self.cidade_input.text().strip()
        email = self.cadastro_email_input.text().strip()
        senha = self.cadastro_password_input.findChild(QLineEdit).text()
        confirmacao = self.confirm_password_input.findChild(QLineEdit).text()

        if not nome or not usuario or not cidade or not email or not senha:
            QMessageBox.warning(self, "Erro", "Todos os campos devem ser preenchidos.")
            return

        if senha != confirmacao:
            QMessageBox.warning(self, "Erro", "As senhas não conferem.")
            return

        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        try:
            user_id = self.usuario_model.cadastrar_usuario(usuario, senha_hash, email, cidade, "comum")
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
