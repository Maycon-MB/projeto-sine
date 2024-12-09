from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QSpinBox, QTextEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
import psycopg2


class CadastroWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("Cadastro de Pessoa")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        main_layout.addWidget(title_label)
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Campos do formulário
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Digite o nome completo")
        form_layout.addRow("Nome:", self.nome_input)

        self.idade_input = QSpinBox()
        self.idade_input.setRange(0, 150)
        self.idade_input.setSuffix(" anos")
        form_layout.addRow("Idade:", self.idade_input)

        self.telefone_input = QLineEdit()
        self.telefone_input.setPlaceholderText("Digite o telefone (ex: (XX) XXXXX-XXXX)")
        form_layout.addRow("Telefone:", self.telefone_input)

        self.experiencia_input = QTextEdit()
        self.experiencia_input.setPlaceholderText("Digite a experiência profissional ou observações")
        form_layout.addRow("Experiência:", self.experiencia_input)

        main_layout.addLayout(form_layout)

        # Botões
        button_layout = QHBoxLayout()
        
        self.salvar_button = QPushButton("Salvar")
        self.salvar_button.clicked.connect(self.salvar_dados)
        self.salvar_button.setStyleSheet("background-color: #0073CF; color: white; padding: 10px;")
        
        self.limpar_button = QPushButton("Limpar")
        self.limpar_button.clicked.connect(self.limpar_formulario)
        self.limpar_button.setStyleSheet("background-color: #dcdcdc; color: black; padding: 10px;")

        button_layout.addWidget(self.salvar_button)
        button_layout.addWidget(self.limpar_button)
        main_layout.addLayout(button_layout)

    def salvar_dados(self):
        # Obter os dados dos campos
        nome = self.nome_input.text().strip()
        idade = self.idade_input.value()
        telefone = self.telefone_input.text().strip()
        experiencia = self.experiencia_input.toPlainText().strip()

        if not nome or idade == 0:
            QMessageBox.warning(self, "Erro", "Por favor, preencha todos os campos obrigatórios.")
            return

        # Conexão com o banco de dados
        try:
            conn = psycopg2.connect(
                dbname="projeto-sine",
                user="postgres",
                password="admin",
                host="localhost"
            )
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pessoas (nome, idade, telefone, experiencia)
                VALUES (%s, %s, %s, %s)
            """, (nome, idade, telefone, experiencia))
            conn.commit()
            cursor.close()
            conn.close()

            QMessageBox.information(self, "Sucesso", "Dados cadastrados com sucesso!")
            self.limpar_formulario()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar dados: {e}")

    def limpar_formulario(self):
        # Limpa todos os campos do formulário
        self.nome_input.clear()
        self.idade_input.setValue(0)
        self.telefone_input.clear()
        self.experiencia_input.clear()
