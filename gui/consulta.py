from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QComboBox, QSpinBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QHeaderView
from database.models import CurriculoModel


class ConsultaWidget(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.curriculo_model = CurriculoModel(self.db_connection)

        self.setWindowTitle("Consultar Currículos")

        # Estilo global reduzido com botões arredondados e menores
        self.setStyleSheet("""
            QLabel, QLineEdit, QComboBox, QSpinBox, QTableWidget {
                font-size: 12px;
            }
            QPushButton {
                font-size: 12px;
                padding: 4px 8px;
                background-color: #0056A1;
                color: white;
                border: none;
                border-radius: 5px;
                width: 100px;
            }
            QPushButton:hover {
                background-color: #004080;
            }
        """)

        # Layout principal
        layout = QVBoxLayout()

        # Filtros
        filter_layout = QVBoxLayout()

        # Primeira linha de filtros
        first_row = QHBoxLayout()
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome")
        first_row.addWidget(QLabel("Nome:"))
        first_row.addWidget(self.nome_input)

        self.escolaridade_input = QComboBox()
        self.escolaridade_input.addItems([
            "", "Ensino Fundamental", "Ensino Médio Incompleto", "Ensino Médio Completo",
            "Ensino Superior Incompleto", "Ensino Superior Completo", "Pós-Graduação/MBA",
            "Mestrado", "Doutorado"
        ])
        first_row.addWidget(QLabel("Escolaridade:"))
        first_row.addWidget(self.escolaridade_input)

        # Segunda linha de filtros
        second_row = QHBoxLayout()
        self.cargo_input = QLineEdit()
        self.cargo_input.setPlaceholderText("Cargo")
        second_row.addWidget(QLabel("Cargo:"))
        second_row.addWidget(self.cargo_input)

        self.experiencia_min_input = QSpinBox()
        self.experiencia_min_input.setRange(0, 50)
        second_row.addWidget(QLabel("Experiência Mínima:"))
        second_row.addWidget(self.experiencia_min_input)

        self.idade_min_input = QSpinBox()
        self.idade_min_input.setRange(0, 120)
        second_row.addWidget(QLabel("Idade Mínima:"))
        second_row.addWidget(self.idade_min_input)

        self.idade_max_input = QSpinBox()
        self.idade_max_input.setRange(0, 120)
        second_row.addWidget(QLabel("Idade Máxima:"))
        second_row.addWidget(self.idade_max_input)

        self.order_by_input = QComboBox()
        self.order_by_input.addItems(["", "nome", "idade", "escolaridade", "cargo", "anos_experiencia"])
        second_row.addWidget(QLabel("Ordenar por:"))
        second_row.addWidget(self.order_by_input)

        # Botões
        button_row = QHBoxLayout()
        button_row.setSpacing(10)

        self.clear_button = QPushButton("Limpar Filtros")
        self.clear_button.clicked.connect(self.clear_filters)
        button_row.addWidget(self.clear_button)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_row.addSpacerItem(spacer)

        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.search_curriculos)
        button_row.addWidget(self.search_button)

        # Adicionar linhas ao layout de filtros
        filter_layout.addLayout(first_row)
        filter_layout.addLayout(second_row)
        filter_layout.addLayout(button_row)

        layout.addLayout(filter_layout)

        # Tabela de resultados
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Agora com 6 colunas
        self.table.setHorizontalHeaderLabels(["Nome", "Idade", "Telefone", "Escolaridade", "Cargo", "Experiência (anos)"])
        self.table.setShowGrid(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)

        # Contagem total de pessoas
        self.total_label = QLabel("Total de pessoas: 0")
        self.total_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.total_label)

        self.setLayout(layout)
        self.install_event_filters()

    def install_event_filters(self):
        widgets = [
            self.nome_input, self.escolaridade_input, self.cargo_input,
            self.experiencia_min_input, self.idade_min_input, self.idade_max_input,
            self.order_by_input, self.search_button, self.clear_button
        ]
        for widget in widgets:
            widget.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and isinstance(event, QKeyEvent):
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.focusNextChild()
                return True
        return super().eventFilter(source, event)

    def search_curriculos(self):
        nome = self.nome_input.text().strip()
        escolaridade = self.escolaridade_input.currentText()
        cargo = self.cargo_input.text().strip()
        experiencia_min = self.experiencia_min_input.value() or None
        idade_min = self.idade_min_input.value() or None
        idade_max = self.idade_max_input.value() or None
        order_by = self.order_by_input.currentText() or None

        try:
            results = self.curriculo_model.fetch_filtered_curriculos(
                nome=nome if nome else None,
                escolaridade=escolaridade if escolaridade else None,
                idade_min=idade_min,
                idade_max=idade_max,
                cargo=cargo if cargo else None,
                experiencia_min=experiencia_min
            )
            if order_by:
                results.sort(key=lambda x: x.get(order_by, ""))

            self.populate_table(results)
        except Exception as e:
            print(f"Erro ao buscar currículos: {e}")

    def populate_table(self, results):
        self.table.setRowCount(len(results))
        for row_idx, row in enumerate(results):
            nome_item = QTableWidgetItem(row['nome'])
            nome_item.setTextAlignment(Qt.AlignCenter)
            nome_item.setToolTip(row['nome'])  # Adiciona tooltip
            self.table.setItem(row_idx, 0, nome_item)

            idade_item = QTableWidgetItem(str(row['idade']))
            idade_item.setTextAlignment(Qt.AlignCenter)
            idade_item.setToolTip(str(row['idade']))  # Adiciona tooltip
            self.table.setItem(row_idx, 1, idade_item)

            telefone_item = QTableWidgetItem(row['telefone'])
            telefone_item.setTextAlignment(Qt.AlignCenter)
            telefone_item.setToolTip(row['telefone'])  # Adiciona tooltip
            self.table.setItem(row_idx, 2, telefone_item)

            escolaridade_item = QTableWidgetItem(row['escolaridade'])
            escolaridade_item.setTextAlignment(Qt.AlignCenter)
            escolaridade_item.setToolTip(row['escolaridade'])  # Adiciona tooltip
            self.table.setItem(row_idx, 3, escolaridade_item)

            cargo_item = QTableWidgetItem(row.get('cargo', ''))
            cargo_item.setTextAlignment(Qt.AlignCenter)
            cargo_item.setToolTip(row.get('cargo', ''))  # Adiciona tooltip
            self.table.setItem(row_idx, 4, cargo_item)

            experiencia_item = QTableWidgetItem(f"{row.get('anos_experiencia', '0')} anos")
            experiencia_item.setTextAlignment(Qt.AlignCenter)
            experiencia_item.setToolTip(f"{row.get('anos_experiencia', '0')} anos")  # Adiciona tooltip
            self.table.setItem(row_idx, 5, experiencia_item)

        self.total_label.setText(f"Total de pessoas: {len(results)}")


    def clear_filters(self):
        self.nome_input.clear()
        self.escolaridade_input.setCurrentIndex(0)
        self.cargo_input.clear()
        self.experiencia_min_input.setValue(0)
        self.idade_min_input.setValue(0)
        self.idade_max_input.setValue(0)
        self.order_by_input.setCurrentIndex(0)
