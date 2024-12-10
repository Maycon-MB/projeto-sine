from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QHBoxLayout, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeyEvent, QIcon
import psycopg2
import re


class DatabaseHandler:
    def __init__(self, dbname, user, password, host):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host

    def connect(self):
        try:
            return psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host
            )
        except Exception as e:
            raise ConnectionError(f"Erro ao conectar ao banco de dados: {e}")

    def is_duplicate(self, nome, telefone):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM pessoas WHERE nome = %s OR telefone = %s",
                (nome, telefone)
            )
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result[0] > 0
        except Exception as e:
            raise RuntimeError(f"Erro ao verificar duplicidade: {e}")

    def insert_pessoa(self, nome, idade, telefone, experiencia, escolaridade, servicos):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pessoas (nome, idade, telefone, experiencia, escolaridade, servicos_realizados)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nome, idade, telefone, experiencia, escolaridade, servicos))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            raise RuntimeError(f"Erro ao inserir dados: {e}")

class CadastroWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db_handler = DatabaseHandler(
            dbname="projeto-sine",
            user="postgres",
            password="admin",
            host="localhost"
        )
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        title_label = QLabel("Cadastro de Currículo")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 1px;")
        main_layout.addWidget(title_label)

        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        # Campos do formulário
        self.nome_input = self.create_line_edit("Digite o nome completo", "Nome:", form_layout, 0)
        self.idade_input = self.create_line_edit("Digite a idade", "Idade:", form_layout, 1)
        self.telefone_input = self.create_line_edit("Digite o telefone (ex: (XX) XXXXX-XXXX)", "Telefone:", form_layout, 2)
        self.escolaridade_input = self.create_line_edit("Digite a escolaridade", "Escolaridade:", form_layout, 3)

        self.experiencia_input = self.create_text_edit("Digite a experiência profissional ou observações", "Experiência:", form_layout, 4)
        self.servicos_input = self.create_text_edit("Digite os serviços realizados", "Serviços Realizados:", form_layout, 5)

        main_layout.addLayout(form_layout)

        # Botões
        button_layout = QHBoxLayout()
        self.cadastrar_button = QPushButton("Cadastrar")
        self.cadastrar_button.clicked.connect(self.cadastrar_dados)
        self.cadastrar_button.setStyleSheet("background-color: #0073CF; color: white; padding: 10px;")
        self.cadastrar_button.setIcon(QIcon("icons/save.png"))

        self.limpar_button = QPushButton("Limpar")
        self.limpar_button.clicked.connect(self.limpar_formulario)
        self.limpar_button.setStyleSheet("background-color: #dcdcdc; color: black; padding: 10px;")
        self.limpar_button.setIcon(QIcon("icons/clear.png"))

        button_layout.addWidget(self.cadastrar_button)
        button_layout.addWidget(self.limpar_button)
        main_layout.addLayout(button_layout)

    def create_line_edit(self, placeholder, label, layout, row):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.installEventFilter(self)  # Instala o Event Filter para capturar Enter
        layout.addWidget(QLabel(label), row, 0)
        layout.addWidget(line_edit, row, 1)
        return line_edit

    def create_text_edit(self, placeholder, label, layout, row):
        text_edit = QTextEdit()
        text_edit.setPlaceholderText(placeholder)
        text_edit.installEventFilter(self)  # Instala o Event Filter para capturar Enter
        text_edit.setFixedHeight(100)
        layout.addWidget(QLabel(label), row, 0)
        layout.addWidget(text_edit, row, 1)
        return text_edit

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return:
            self.focusNextChild()  # Move o foco para o próximo widget
            return True
        return super().eventFilter(source, event)

    def cadastrar_dados(self):
        nome = self.nome_input.text().strip()
        idade = self.idade_input.text().strip()
        telefone = self.telefone_input.text().strip()
        escolaridade = self.escolaridade_input.text().strip()
        experiencia = self.experiencia_input.toPlainText().strip()
        servicos = self.servicos_input.toPlainText().strip()

        if not nome or not idade or not telefone or not escolaridade:
            QMessageBox.warning(self, "Erro", "Por favor, preencha todos os campos obrigatórios.")
            return

        if not self.validar_telefone(telefone):
            QMessageBox.warning(self, "Erro", "Telefone inválido! Use o formato (XX) XXXXX-XXXX.")
            return

        try:
            if self.db_handler.is_duplicate(nome, telefone):
                QMessageBox.warning(self, "Erro", "Pessoa já cadastrada com este nome ou telefone.")
                return

            self.db_handler.insert_pessoa(nome, idade, telefone, experiencia, escolaridade, servicos)
            QMessageBox.information(self, "Sucesso", "Dados cadastrados com sucesso!")
            self.limpar_formulario()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def limpar_formulario(self):
        resposta = QMessageBox.question(
            self, "Confirmação", "Deseja realmente limpar o formulário?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resposta == QMessageBox.Yes:
            self.nome_input.clear()
            self.idade_input.clear()
            self.telefone_input.clear()
            self.escolaridade_input.clear()
            self.experiencia_input.clear()
            self.servicos_input.clear()

    def validar_telefone(self, telefone):
        pattern = r"^\(\d{2}\) \d{4,5}-\d{4}$"
        return re.match(pattern, telefone)
