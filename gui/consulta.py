from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QSpinBox
)
from database.models import CurriculoModel
from database.connection import DatabaseConnection

class ConsultaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_database()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Filtros
        filters_layout = QHBoxLayout()
        
        filters_layout.addWidget(QLabel("Nome:"))
        self.nome_input = QLineEdit()
        filters_layout.addWidget(self.nome_input)

        filters_layout.addWidget(QLabel("Escolaridade:"))
        self.escolaridade_input = QComboBox()
        self.escolaridade_input.addItems(["", "Ensino Fundamental", "Ensino Médio", "Ensino Superior", "Pós-Graduação"])
        filters_layout.addWidget(self.escolaridade_input)

        filters_layout.addWidget(QLabel("Idade Mínima:"))
        self.idade_min_input = QSpinBox()
        self.idade_min_input.setMinimum(0)
        filters_layout.addWidget(self.idade_min_input)

        filters_layout.addWidget(QLabel("Idade Máxima:"))
        self.idade_max_input = QSpinBox()
        self.idade_max_input.setMinimum(0)
        filters_layout.addWidget(self.idade_max_input)

        search_button = QPushButton("Buscar")
        search_button.clicked.connect(self.search_curriculos)
        filters_layout.addWidget(search_button)

        layout.addLayout(filters_layout)

        # Tabela de resultados
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(["ID", "Nome", "Idade", "Telefone", "Escolaridade"])
        layout.addWidget(self.result_table)

        # Botão para editar
        edit_button = QPushButton("Editar Selecionado")
        edit_button.clicked.connect(self.edit_selected)
        layout.addWidget(edit_button)

    def setup_database(self):
        # Configurar conexão com o banco e modelo
        self.db_connection = DatabaseConnection(
            dbname="BOLETOS", user="postgres", password="postgres", host="192.168.1.163"
        )
        self.curriculo_model = CurriculoModel(self.db_connection)

    def search_curriculos(self):
        nome = self.nome_input.text()
        escolaridade = self.escolaridade_input.currentText()
        idade_min = self.idade_min_input.value()
        idade_max = self.idade_max_input.value()

        results = self.curriculo_model.fetch_all_curriculos(
            nome=nome,
            escolaridade=escolaridade if escolaridade else None,
            idade_min=idade_min if idade_min > 0 else None,
            idade_max=idade_max if idade_max > 0 else None
        )

        self.populate_table(results)

    def populate_table(self, data):
        self.result_table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            self.result_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data['id'])))
            self.result_table.setItem(row_idx, 1, QTableWidgetItem(row_data['nome']))
            self.result_table.setItem(row_idx, 2, QTableWidgetItem(str(row_data['idade'])))
            self.result_table.setItem(row_idx, 3, QTableWidgetItem(row_data['telefone']))
            self.result_table.setItem(row_idx, 4, QTableWidgetItem(row_data['escolaridade']))

    def edit_selected(self):
        selected_row = self.result_table.currentRow()
        if selected_row >= 0:
            curriculo_id = self.result_table.item(selected_row, 0).text()
            print(f"Editar o currículo com ID: {curriculo_id}")
            # Aqui você pode abrir a tela de edição e carregar os dados correspondentes
