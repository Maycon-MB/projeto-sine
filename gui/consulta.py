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
        self.escolaridade_input.addItems([
            "", "Ensino Fundamental", "Ensino Médio Incompleto", "Ensino Médio Completo",
            "Ensino Superior Incompleto", "Ensino Superior Completo", "Pós-Graduação/MBA",
            "Mestrado", "Doutorado"
        ])
        filter_layout.addWidget(QLabel("Escolaridade:"))
        filter_layout.addWidget(self.escolaridade_input)

        self.idade_min_input = QSpinBox()
        self.idade_min_input.setRange(0, 120)
        self.idade_min_input.setPrefix("Min: ")
        filter_layout.addWidget(QLabel("Idade Mínima:"))
        filter_layout.addWidget(self.idade_min_input)

        self.idade_max_input = QSpinBox()
        self.idade_max_input.setRange(0, 120)
        self.idade_max_input.setPrefix("Max: ")
        filter_layout.addWidget(QLabel("Idade Máxima:"))
        filter_layout.addWidget(self.idade_max_input)

        self.order_by_input = QComboBox()
        self.order_by_input.addItems(["", "nome", "idade", "escolaridade"])
        filter_layout.addWidget(QLabel("Ordenar por:"))
        filter_layout.addWidget(self.order_by_input)

        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.search_curriculos)
        filter_layout.addWidget(self.search_button)

        layout.addLayout(filter_layout)

        # Tabela de resultados
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Ajustado para incluir todas as colunas necessárias
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Idade", "Telefone", "Escolaridade", "Experiência"])
        layout.addWidget(self.table)

        self.setLayout(layout)

    def search_curriculos(self):
        # Coletar os filtros fornecidos pelo usuário
        nome = self.nome_input.text().strip()
        escolaridade = self.escolaridade_input.currentText()
        idade_min = self.idade_min_input.value() or None
        idade_max = self.idade_max_input.value() or None
        order_by = self.order_by_input.currentText() or None

        # Buscar currículos no banco de dados
        try:
            results = self.curriculo_model.fetch_filtered_curriculos(
                nome=nome if nome else None,
                escolaridade=escolaridade if escolaridade else None,
                idade_min=idade_min,
                idade_max=idade_max
            )
            # Ordenar os resultados se necessário
            if order_by:
                results.sort(key=lambda x: x.get(order_by))

            self.populate_table(results)
        except Exception as e:
            print(f"Erro ao buscar currículos: {e}")

    def populate_table(self, results):
        """
        Preenche a tabela com os resultados da consulta.
        """
        self.table.setRowCount(len(results))
        for row_idx, row in enumerate(results):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row['curriculo_id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row['nome']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(row['idade'])))
            self.table.setItem(row_idx, 3, QTableWidgetItem(row['telefone']))
            self.table.setItem(row_idx, 4, QTableWidgetItem(row['escolaridade']))

            # Concatenar experiências para exibição
            experiencia_text = f"{row.get('cargo', '')} - {row.get('anos_experiencia', '')} anos"
            self.table.setItem(row_idx, 5, QTableWidgetItem(experiencia_text))
