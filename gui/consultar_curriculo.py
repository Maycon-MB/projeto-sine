from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QComboBox, QSpinBox, QMessageBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView
from database.models import CurriculoModel
from gui.editar_curriculo import EditDialog


class ConsultaWidget(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.curriculo_model = CurriculoModel(self.db_connection)
        self.model = CurriculoModel(self.db_connection)  # Inicializa o model para integração

        self.setWindowTitle("Consultar Currículos")
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface gráfica."""
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

        layout = QVBoxLayout()

        # Filtros
        filter_layout = self.create_filter_layout()
        layout.addLayout(filter_layout)

        # Tabela de resultados
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Nome", "Idade", "Telefone", "Escolaridade", "Cargo", "Experiência (anos)"])
        self.table.setShowGrid(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Contagem total
        self.total_label = QLabel("Total de pessoas: 0")
        self.total_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.total_label)

        self.setLayout(layout)

    def create_filter_layout(self):
        """Cria o layout de filtros e botões."""
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

        self.status_input = QComboBox()
        self.status_input.addItems(["Todos", "disponível", "empregado", "não disponível"])
        second_row.addWidget(QLabel("Status:"))
        second_row.addWidget(self.status_input)


        # Botões de controle
        button_row = QHBoxLayout()

        # Botão de Buscar (à esquerda)
        self.search_button = QPushButton("Buscar")
        self.search_button.setFixedSize(100, 30)
        self.search_button.clicked.connect(self.search_curriculos)
        button_row.addWidget(self.search_button)

        # Espaçamento entre os botões
        button_row.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding))

        # Botão de Editar (no centro)
        self.edit_button = QPushButton("Editar Currículo")
        self.edit_button.setFixedSize(100, 30)
        self.edit_button.clicked.connect(self.edit_selected_row)
        button_row.addWidget(self.edit_button)

        # Mais um espaçador
        button_row.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding))

        # Botão de Limpar Filtros (à direita)
        self.clear_button = QPushButton("Limpar Filtros")
        self.clear_button.setFixedSize(100, 30)
        self.clear_button.clicked.connect(self.clear_filters)
        button_row.addWidget(self.clear_button)

        # Adicionar linhas ao layout de filtros
        filter_layout.addLayout(first_row)
        filter_layout.addLayout(second_row)
        filter_layout.addLayout(button_row)

        return filter_layout

    def search_curriculos(self):
        """Busca currículos aplicando os filtros especificados, incluindo status."""
        nome = self.nome_input.text().strip()
        escolaridade = self.escolaridade_input.currentText()
        cargo = self.cargo_input.text().strip()
        experiencia_min = self.experiencia_min_input.value() or None
        idade_min = self.idade_min_input.value() or None
        idade_max = self.idade_max_input.value() or None
        status = self.status_input.currentText()

        try:
            results = self.curriculo_model.fetch_filtered_curriculos(
                nome=nome if nome else None,
                escolaridade=escolaridade if escolaridade else None,
                idade_min=idade_min,
                idade_max=idade_max,
                cargo=cargo if cargo else None,
                experiencia_min=experiencia_min,
                status=status
            )
            self.populate_table(results)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao buscar currículos: {e}")

    def populate_table(self, results):
        """Popula a tabela com os resultados da busca."""
        self.table.setColumnCount(7)  # Inclui a coluna "ID" oculta
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Idade", "Telefone", "Escolaridade", "Cargo", "Experiência (anos)"])
        self.table.setRowCount(len(results))

        for row_idx, row in enumerate(results):
            # Coluna de ID (oculta)
            id_item = QTableWidgetItem(str(row['curriculo_id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setToolTip(str(row['curriculo_id']))  # Tooltip para a coluna ID
            self.table.setItem(row_idx, 0, id_item)

            # Outras colunas
            nome_item = QTableWidgetItem(row['nome'])
            nome_item.setTextAlignment(Qt.AlignCenter)
            nome_item.setToolTip(row['nome'])  # Tooltip para o nome
            self.table.setItem(row_idx, 1, nome_item)

            idade_item = QTableWidgetItem(str(row['idade']))
            idade_item.setTextAlignment(Qt.AlignCenter)
            idade_item.setToolTip(str(row['idade']))  # Tooltip para a idade
            self.table.setItem(row_idx, 2, idade_item)

            telefone_item = QTableWidgetItem(row['telefone'])
            telefone_item.setTextAlignment(Qt.AlignCenter)
            telefone_item.setToolTip(row['telefone'])  # Tooltip para o telefone
            self.table.setItem(row_idx, 3, telefone_item)

            escolaridade_item = QTableWidgetItem(row['escolaridade'])
            escolaridade_item.setTextAlignment(Qt.AlignCenter)
            escolaridade_item.setToolTip(row['escolaridade'])  # Tooltip para a escolaridade
            self.table.setItem(row_idx, 4, escolaridade_item)

            cargo_item = QTableWidgetItem(row.get('cargo', ''))
            cargo_item.setTextAlignment(Qt.AlignCenter)
            cargo_item.setToolTip(row.get('cargo', ''))  # Tooltip para o cargo
            self.table.setItem(row_idx, 5, cargo_item)

            experiencia_item = QTableWidgetItem(f"{row.get('anos_experiencia', '0')} anos")
            experiencia_item.setTextAlignment(Qt.AlignCenter)
            experiencia_item.setToolTip(f"{row.get('anos_experiencia', '0')} anos")  # Tooltip para experiência
            self.table.setItem(row_idx, 6, experiencia_item)

        # Ocultar a coluna de ID
        self.table.setColumnHidden(0, True)

        self.total_label.setText(f"Total de pessoas: {len(results)}")

    def edit_selected_row(self):
        """Abre o diálogo para editar a linha selecionada."""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione uma linha para editar.")
            return

        selected_row = selected_items[0].row()
        curriculo_id = int(self.table.item(selected_row, 0).text())  # ID agora está na coluna 0
        self.open_edit_dialog(curriculo_id)

    def open_edit_dialog(self, curriculo_id):
        """Abre o diálogo para editar um currículo."""
        dialog = EditDialog(self.curriculo_model, curriculo_id, self)
        if dialog.exec():
            self.search_curriculos()

    def clear_filters(self):
        """Limpa os filtros de busca."""
        self.nome_input.clear()
        self.escolaridade_input.setCurrentIndex(0)
        self.cargo_input.clear()
        self.experiencia_min_input.setValue(0)
        self.idade_min_input.setValue(0)
        self.idade_max_input.setValue(0)
