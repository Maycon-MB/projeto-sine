from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeyEvent
from database.curriculo_model import CurriculoModel


class EditDialog(QDialog):
    def __init__(self, curriculo_model, curriculo_id, parent=None):
        super().__init__(parent)
        self.curriculo_model = curriculo_model
        self.curriculo_id = curriculo_id

        self.setWindowTitle("EDITAR CURRÍCULO")
        self.setup_ui()
        self.load_curriculo_data()

    def setup_ui(self):
        self.setLayout(QVBoxLayout())

        # Campos para edição
        self.nome_input = QLineEdit()
        self.nome_input.textChanged.connect(lambda text: self.nome_input.setText(text.upper()))
        self.idade_input = QSpinBox()
        self.idade_input.setRange(0, 120)
        self.telefone_input = QLineEdit()
        self.telefone_input.textChanged.connect(lambda text: self.telefone_input.setText(text.upper()))
        self.escolaridade_input = QComboBox()
        self.escolaridade_input.addItems([
            "ENSINO FUNDAMENTAL", "ENSINO MÉDIO INCOMPLETO", "ENSINO MÉDIO COMPLETO",
            "ENSINO SUPERIOR INCOMPLETO", "ENSINO SUPERIOR COMPLETO", "PÓS-GRADUAÇÃO/MBA",
            "MESTRADO", "DOUTORADO"
        ])
        self.cargo_input = QLineEdit()
        self.cargo_input.textChanged.connect(lambda text: self.cargo_input.setText(text.upper()))
        self.anos_experiencia_input = QSpinBox()
        self.anos_experiencia_input.setRange(0, 50)
        
        # Novo campo: Status
        self.status_input = QComboBox()
        self.status_input.addItems(["DISPONÍVEL", "EMPREGRADO", "NÃO DISPONÍVEL"])

        # Adicionando os campos
        self.layout().addWidget(QLabel("NOME:"))
        self.layout().addWidget(self.nome_input)
        self.layout().addWidget(QLabel("IDADE:"))
        self.layout().addWidget(self.idade_input)
        self.layout().addWidget(QLabel("TELEFONE:"))
        self.layout().addWidget(self.telefone_input)
        self.layout().addWidget(QLabel("ESCOLARIDADE:"))
        self.layout().addWidget(self.escolaridade_input)
        self.layout().addWidget(QLabel("CARGO:"))
        self.layout().addWidget(self.cargo_input)
        self.layout().addWidget(QLabel("ANOS DE EXPERIÊNCIA:"))
        self.layout().addWidget(self.anos_experiencia_input)
        self.layout().addWidget(QLabel("STATUS:"))
        self.layout().addWidget(self.status_input)

        # Botões
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("SALVAR")
        self.save_button.clicked.connect(self.save_changes)
        self.cancel_button = QPushButton("CANCELAR")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        self.layout().addLayout(button_layout)

        # Ativar transição com Enter
        self.configurar_transicao_enter([
            self.nome_input, self.idade_input, self.telefone_input,
            self.escolaridade_input, self.cargo_input, self.anos_experiencia_input, self.status_input
        ])

    def configurar_transicao_enter(self, widgets):
        for i, widget in enumerate(widgets):
            widget.setProperty("index", i)
            widget.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and isinstance(event, QKeyEvent):
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                current_index = source.property("index")
                if current_index is not None:
                    next_index = current_index + 1
                    widgets = source.parentWidget().findChildren(QLineEdit) + source.parentWidget().findChildren(QComboBox)
                    if next_index < len(widgets):
                        widgets[next_index].setFocus()
                        return True
        return super().eventFilter(source, event)

    def load_curriculo_data(self):
        try:
            curriculo = self.curriculo_model.get_curriculo_by_id(self.curriculo_id)
            experiencias = self.curriculo_model.fetch_experiencias(self.curriculo_id)
            if curriculo:
                self.nome_input.setText(curriculo.get("nome", ""))
                self.idade_input.setValue(curriculo.get("idade", 0))
                self.telefone_input.setText(curriculo.get("telefone", ""))
                self.escolaridade_input.setCurrentText(curriculo.get("escolaridade", ""))
                self.status_input.setCurrentText(curriculo.get("status", ""))
                if experiencias:
                    self.cargo_input.setText(experiencias[0].get("cargo", ""))
                    self.anos_experiencia_input.setValue(experiencias[0].get("anos_experiencia", 0))
            else:
                QMessageBox.warning(self, "AVISO", "CURRÍCULO NÃO ENCONTRADO.")
                self.reject()
        except Exception as e:
            QMessageBox.critical(self, "ERRO", f"ERRO AO CARREGAR DADOS: {e}")
            self.reject()

    def save_changes(self):
        nome = self.nome_input.text().strip().upper()
        idade = self.idade_input.value()
        telefone = self.telefone_input.text().strip().upper()
        escolaridade = self.escolaridade_input.currentText().upper()
        cargo = self.cargo_input.text().strip().upper()
        anos_experiencia = self.anos_experiencia_input.value()
        status = self.status_input.currentText().upper()

        if not nome or not telefone or not escolaridade or not cargo or not status:
            QMessageBox.warning(self, "AVISO", "TODOS OS CAMPOS DEVEM SER PREENCHIDOS.")
            return

        confirmacao = QMessageBox.question(
            self, "CONFIRMAÇÃO", "DESEJA SALVAR AS ALTERAÇÕES?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmacao == QMessageBox.Yes:
            try:
                self.curriculo_model.update_curriculo(
                    self.curriculo_id, nome, idade, telefone, escolaridade, status
                )
                self.curriculo_model.insert_experiencias(
                    self.curriculo_id, [(cargo, anos_experiencia)]
                )
                QMessageBox.information(self, "SUCESSO", "CURRÍCULO ATUALIZADO COM SUCESSO!")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "ERRO", f"ERRO AO SALVAR ALTERAÇÕES: {e}")
