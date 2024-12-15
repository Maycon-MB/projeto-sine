from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt
from database.models import CurriculoModel

class ConsultaWidget(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.curriculo_model = CurriculoModel(self.db_connection)

        self.setWindowTitle("Consultar Currículos")

        # Layout principal
        layout = QVBoxLayout()

        # Filtros
        filter_layout = QHBoxLayout()

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome")
        filter_layout.addWidget(QLabel("Nome:"))
        filter_layout.addWidget(self.nome_input)

        self.escolaridade_input = QComboBox()
        self.escolaridade_input.addItems(["", "Ensino Fundamental", "Ensino Médio", "Ensino Superior"])
        filter_layout.addWidget(QLabel("Escolaridade:"))
        filter_layout.addWidget(self.escolaridade_input)

        self.idade_min_input = QSpinBox()
        self.idade_min_input.setRange(0, 120)
        self.idade_min_input.setPlaceholderText("Idade Min")
        filter_layout.addWidget(QLabel("Idade Mínima:"))
        filter_layout.addWidget(self.idade_min_input)

        self.idade_max_input = QSpinBox()
        self.idade_max_input.setRange(0, 120)
        self.idade_max_input.setPlaceholderText("Idade Max")
        filter_layout.addWidget(QLabel("Idade Máxima:"))
        filter_layout.addWidget(self.idade_max_input)

        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.search_curriculos)
        filter_layout.addWidget(self.search_button)

        layout.addLayout(filter_layout)

        # Tabela de resultados
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nome", "Idade", "Telefone", "Escolaridade"])
        layout.addWidget(self.table)

        self.setLayout(layout)

    def search_curriculos(self):
        nome = self.nome_input.text()
        escolaridade = self.escolaridade_input.currentText()
        idade_min = self.idade_min_input.value() or None
        idade_max = self.idade_max_input.value() or None

        results = self.curriculo_model.fetch_all_curriculos(
            nome=nome,
            escolaridade=escolaridade if escolaridade else None,
            idade_min=idade_min,
            idade_max=idade_max
        )

        self.populate_table(results)

    def populate_table(self, results):
        self.table.setRowCount(len(results))
        for row_idx, row in enumerate(results):
            self.table.setItem(row_idx, 0, QTableWidgetItem(row['nome']))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(row['idade'])))
            self.table.setItem(row_idx, 2, QTableWidgetItem(row['telefone']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(row['escolaridade']))
