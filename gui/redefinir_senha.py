from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from hashlib import sha256
import logging

class ResetSenhaDialog(QDialog):
    def __init__(self, usuario_model):
        super().__init__()
        self.usuario_model = usuario_model
        self.setWindowTitle("Recuperação de Senha")
        self.setMinimumSize(400, 200)

        layout = QVBoxLayout(self)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Digite seu e-mail")
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Digite o token recebido")
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Nova senha")
        self.new_password_input.setEchoMode(QLineEdit.Password)

        self.token_button = QPushButton("Solicitar Token")
        self.token_button.clicked.connect(self.solicitar_token)

        self.reset_button = QPushButton("Redefinir Senha")
        self.reset_button.clicked.connect(self.redefinir_senha)

        layout.addWidget(QLabel("E-mail:"))
        layout.addWidget(self.email_input)
        layout.addWidget(self.token_button)
        layout.addWidget(QLabel("Token:"))
        layout.addWidget(self.token_input)
        layout.addWidget(QLabel("Nova Senha:"))
        layout.addWidget(self.new_password_input)
        layout.addWidget(self.reset_button)

    def solicitar_token(self):
        email = self.email_input.text().strip().upper()
        if not email:
            QMessageBox.warning(self, "Erro", "Digite o e-mail.")
            return
        try:
            token = self.usuario_model.gerar_token_recuperacao(email)
            QMessageBox.information(self, "Sucesso", f"Token enviado para {email}.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao solicitar token: {e}")

    def redefinir_senha(self):
        token = self.token_input.text().strip()
        nova_senha = self.new_password_input.text().strip()
        if not token or not nova_senha:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return
        try:
            senha_hash = sha256(nova_senha.encode()).hexdigest()
            self.usuario_model.redefinir_senha(token, senha_hash)
            QMessageBox.information(self, "Sucesso", "Senha redefinida com sucesso!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao redefinir senha: {e}")
