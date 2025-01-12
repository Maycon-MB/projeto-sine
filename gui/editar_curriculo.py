from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton, QComboBox, QMessageBox
)
from database.curriculo_model import CurriculoModel


class EditDialog(QDialog):
    def __init__(self, curriculo_model, curriculo_id, parent=None):
        """
        Construtor do diálogo de edição.
        :param curriculo_model: Modelo de dados para operações no banco.
        :param curriculo_id: ID do currículo a ser editado.
        :param parent: Widget pai (opcional).
        """
        super().__init__(parent)
        self.curriculo_model = curriculo_model
        self.curriculo_id = curriculo_id

        self.setWindowTitle("Editar Currículo")
        self.setup_ui()
        self.load_curriculo_data()

    def setup_ui(self):
        """Configura a interface do diálogo."""
        self.setLayout(QVBoxLayout())

        # Campos para edição
        self.nome_input = QLineEdit()
        self.idade_input = QSpinBox()
        self.idade_input.setRange(0, 120)
        self.telefone_input = QLineEdit()
        self.escolaridade_input = QComboBox()
        self.escolaridade_input.addItems([
            "Ensino Fundamental", "Ensino Médio Incompleto", "Ensino Médio Completo",
            "Ensino Superior Incompleto", "Ensino Superior Completo", "Pós-Graduação/MBA",
            "Mestrado", "Doutorado"
        ])

        self.cargo_input = QLineEdit()
        self.anos_experiencia_input = QSpinBox()
        self.anos_experiencia_input.setRange(0, 50)

        # Layout e labels
        self.layout().addWidget(QLabel("Nome:"))
        self.layout().addWidget(self.nome_input)
        self.layout().addWidget(QLabel("Idade:"))
        self.layout().addWidget(self.idade_input)
        self.layout().addWidget(QLabel("Telefone:"))
        self.layout().addWidget(self.telefone_input)
        self.layout().addWidget(QLabel("Escolaridade:"))
        self.layout().addWidget(self.escolaridade_input)
        self.layout().addWidget(QLabel("Cargo:"))
        self.layout().addWidget(self.cargo_input)
        self.layout().addWidget(QLabel("Anos de Experiência:"))
        self.layout().addWidget(self.anos_experiencia_input)

        # Botões
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_changes)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        self.layout().addLayout(button_layout)

    def load_curriculo_data(self):
        """Carrega os dados do currículo no formulário."""
        try:
            curriculo = self.curriculo_model.get_curriculo_by_id(self.curriculo_id)
            experiencias = self.curriculo_model.fetch_experiencias(self.curriculo_id)
            if curriculo:
                self.nome_input.setText(curriculo.get("nome", ""))
                self.idade_input.setValue(curriculo.get("idade", 0))
                self.telefone_input.setText(curriculo.get("telefone", ""))
                self.escolaridade_input.setCurrentText(curriculo.get("escolaridade", ""))
                if experiencias:
                    self.cargo_input.setText(experiencias[0].get("cargo", ""))
                    self.anos_experiencia_input.setValue(experiencias[0].get("anos_experiencia", 0))
            else:
                QMessageBox.warning(self, "Aviso", "Currículo não encontrado.")
                self.reject()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados: {e}")
            self.reject()

    def save_changes(self):
        """
        Salva as alterações no banco de dados.
        """
        try:
            nome = self.nome_input.text().strip()
            idade = self.idade_input.value()
            telefone = self.telefone_input.text().strip()
            escolaridade = self.escolaridade_input.currentText()
            cargo = self.cargo_input.text().strip()
            anos_experiencia = self.anos_experiencia_input.value()

            if not nome or not telefone or not escolaridade or not cargo:
                QMessageBox.warning(self, "Aviso", "Todos os campos devem ser preenchidos.")
                return

            # Atualizar os dados no banco
            self.curriculo_model.update_curriculo(
                self.curriculo_id,
                nome=nome,
                idade=idade,
                telefone=telefone,
                escolaridade=escolaridade
            )
            # Inserir experiências
            self.curriculo_model.insert_experiencias(
                self.curriculo_id,
                [(cargo, anos_experiencia)]
            )
            QMessageBox.information(self, "Sucesso", "Currículo atualizado com sucesso!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar alterações: {e}")
