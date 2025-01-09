from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from hashlib import sha256

class ResetSenhaDialog(QDialog):
    def __init__(self, usuario_model):
        super().__init__()
        self.usuario_model = usuario_model
        self.setWindowTitle("Recuperação de Senha")

        layout = QVBoxLayout(self)

        # Entrada de e-mail para solicitação de token
        self.email_label = QLabel("Digite seu e-mail:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("E-mail cadastrado")
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)

        self.token_button = QPushButton("Solicitar Token")
        self.token_button.clicked.connect(self.solicitar_token)
        layout.addWidget(self.token_button)

        # Entrada de token e nova senha para redefinição
        self.token_label = QLabel("Digite o token recebido:")
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Token")
        layout.addWidget(self.token_label)
        layout.addWidget(self.token_input)

        self.new_password_label = QLabel("Digite a nova senha:")
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Nova senha")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_password_label)
        layout.addWidget(self.new_password_input)

        self.reset_button = QPushButton("Redefinir Senha")
        self.reset_button.clicked.connect(self.redefinir_senha)
        layout.addWidget(self.reset_button)

    def solicitar_token(self):
        """Solicita o token de recuperação."""
        email = self.email_input.text().strip()
        if not email:
            QMessageBox.warning(self, "Erro", "Por favor, digite o e-mail.")
            return

        try:
            self.usuario_model.gerar_token_recuperacao(email)
            QMessageBox.information(self, "Sucesso", f"Token enviado para o e-mail {email}.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao solicitar token: {e}")

    def redefinir_senha(self):
        """Redefine a senha usando o token."""
        token = self.token_input.text().strip()
        nova_senha = self.new_password_input.text().strip()

        if not token or not nova_senha:
            QMessageBox.warning(self, "Erro", "Por favor, preencha todos os campos.")
            return

        try:
            nova_senha_hash = sha256(nova_senha.encode()).hexdigest()
            self.usuario_model.redefinir_senha(token, nova_senha_hash)
            QMessageBox.information(self, "Sucesso", "Senha redefinida com sucesso!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao redefinir senha: {e}")
