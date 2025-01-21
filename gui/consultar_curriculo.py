from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QComboBox, QSpinBox, QMessageBox, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView
from models.curriculo_model import CurriculoModel
from gui.editar_curriculo import EditDialog


class ConsultaWidget(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.curriculo_model = CurriculoModel(self.db_connection)
        self.model = CurriculoModel(self.db_connection)

        self.setWindowTitle("CONSULTAR CURRÍCULOS")
        self.setup_ui()
        self.search_curriculos()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Filtros de busca
        filter_layout = self.create_filter_layout()
        layout.addLayout(filter_layout)

        # Tabela de resultados
        self.table = QTableWidget()
        self.table.setColumnCount(10)  # Número de colunas ajustado para incluir novos campos
        self.table.setHorizontalHeaderLabels([
            "NOME", "IDADE", "TELEFONE", "CIDADE", "ESCOLARIDADE", 
            "CARGO", "ANOS EXP.", "CTPS", "VAGA ENCAMINHADA", "AÇÕES"
        ])
        self.table.setShowGrid(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Total de resultados
        self.total_label = QLabel("TOTAL DE CURRÍCULOS: 0")
        self.total_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.total_label)

        self.setLayout(layout)


    def create_filter_layout(self):
        filter_layout = QVBoxLayout()

        # Linha 1: Nome, Cidade e Escolaridade
        first_row = QHBoxLayout()
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("NOME")
        self.nome_input.textChanged.connect(lambda text: self.nome_input.setText(text.upper()))
        first_row.addWidget(QLabel("NOME:"))
        first_row.addWidget(self.nome_input)

        self.cidade_input = QComboBox()
        self.cidade_input.addItem("")  # Opção de "todos"
        # Obtém as cidades e as adiciona ao combo box
        cidades = self.curriculo_model.listar_cidades()
        for cidade in cidades:
            self.cidade_input.addItem(cidade)  # `cidade` já é uma string
        first_row.addWidget(QLabel("CIDADE:"))
        first_row.addWidget(self.cidade_input)

        self.escolaridade_input = QComboBox()
        self.escolaridade_input.addItems([
            "", "ENSINO FUNDAMENTAL", "ENSINO MÉDIO", "ENSINO SUPERIOR", 
            "PÓS-GRADUAÇÃO", "MESTRADO", "DOUTORADO"
        ])
        first_row.addWidget(QLabel("ESCOLARIDADE:"))
        first_row.addWidget(self.escolaridade_input)

        # Linha 2: Cargo, Experiência e Idade
        second_row = QHBoxLayout()
        self.cargo_input = QLineEdit()
        self.cargo_input.setPlaceholderText("CARGO")
        self.cargo_input.textChanged.connect(lambda text: self.cargo_input.setText(text.upper()))
        second_row.addWidget(QLabel("CARGO:"))
        second_row.addWidget(self.cargo_input)

        self.experiencia_min_input = QSpinBox()
        self.experiencia_min_input.setRange(0, 50)
        second_row.addWidget(QLabel("EXPERIÊNCIA (MIN.):"))
        second_row.addWidget(self.experiencia_min_input)

        self.idade_min_input = QSpinBox()
        self.idade_min_input.setRange(0, 120)
        second_row.addWidget(QLabel("IDADE MÍNIMA:"))
        second_row.addWidget(self.idade_min_input)

        self.idade_max_input = QSpinBox()
        self.idade_max_input.setRange(0, 120)
        second_row.addWidget(QLabel("IDADE MÁXIMA:"))
        second_row.addWidget(self.idade_max_input)

        # Linha 3: CTPS e Vaga Encaminhada
        third_row = QHBoxLayout()
        self.ctps_input = QComboBox()
        self.ctps_input.addItems(["TODOS", "COM CTPS", "SEM CTPS"])
        third_row.addWidget(QLabel("CTPS:"))
        third_row.addWidget(self.ctps_input)

        self.vaga_encaminhada_input = QComboBox()
        self.vaga_encaminhada_input.addItems(["", "SINE", "MANUAL"])
        third_row.addWidget(QLabel("VAGA ENCAMINHADA:"))
        third_row.addWidget(self.vaga_encaminhada_input)

        # Botões
        button_row = QHBoxLayout()
        self.search_button = QPushButton("BUSCAR")
        self.search_button.clicked.connect(self.search_curriculos)
        button_row.addWidget(self.search_button)

        self.clear_button = QPushButton("LIMPAR FILTROS")
        self.clear_button.clicked.connect(self.clear_filters)
        button_row.addWidget(self.clear_button)

        # Adicionar tudo ao layout principal de filtros
        filter_layout.addLayout(first_row)
        filter_layout.addLayout(second_row)
        filter_layout.addLayout(third_row)
        filter_layout.addLayout(button_row)

        return filter_layout

    def search_curriculos(self):
        # Coleta os valores dos filtros
        filtros = {
            "nome": self.nome_input.text().strip() or None,
            "cidade": self.cidade_input.currentText() or None,
            "escolaridade": self.escolaridade_input.currentText() or None,
            "cargo": self.cargo_input.text().strip() or None,
            "experiencia_min": self.experiencia_min_input.value() or None,
            "idade_min": self.idade_min_input.value() or None,
            "idade_max": self.idade_max_input.value() or None,
            "ctps": self.ctps_input.currentText(),
            "vaga_encaminhada": self.vaga_encaminhada_input.currentText()
        }

        # Mapeia CTPS para True/False
        if filtros["ctps"] == "COM CTPS":
            filtros["ctps"] = True
        elif filtros["ctps"] == "SEM CTPS":
            filtros["ctps"] = False
        else:
            filtros["ctps"] = None

        # Busca os currículos no modelo
        results = self.curriculo_model.fetch_curriculos(filtros)
        self.populate_table(results)

    def populate_table(self, results):
        self.table.setRowCount(len(results))
        for row_idx, row in enumerate(results):
            # Preenche as colunas da tabela
            for col_idx, key in enumerate([
                "nome", "idade", "telefone", "cidade", "escolaridade",
                "cargo", "anos_experiencia", "tem_ctps", "vaga_encaminhada"
            ]):
                value = "Sim" if key == "tem_ctps" and row.get(key) else row.get(key, "")
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

            # Botão de edição
            edit_button = QPushButton("EDITAR")
            edit_button.clicked.connect(lambda _, id=row["curriculo_id"]: self.open_edit_dialog(id))
            self.table.setCellWidget(row_idx, 9, edit_button)

        self.total_label.setText(f"TOTAL DE CURRÍCULOS: {len(results)}")


    def open_edit_dialog(self, curriculo_id):
        dialog = EditDialog(self.curriculo_model, curriculo_id, self)
        if dialog.exec():
            self.search_curriculos()

    def clear_filters(self):
        self.nome_input.clear()
        self.cidade_input.setCurrentIndex(0)
        self.escolaridade_input.setCurrentIndex(0)
        self.cargo_input.clear()
        self.experiencia_min_input.setValue(0)
        self.idade_min_input.setValue(0)
        self.idade_max_input.setValue(0)
        self.ctps_input.setCurrentIndex(0)
        self.vaga_encaminhada_input.setCurrentIndex(0)
        self.search_curriculos()