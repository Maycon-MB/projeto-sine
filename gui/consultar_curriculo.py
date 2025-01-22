from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QGridLayout, QFrame, 
    QTableWidget, QTableWidgetItem, QComboBox, QSpinBox, QMessageBox
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

        # Variáveis para paginação
        self.current_page = 0
        self.items_per_page = 10
        self.total_results = 0

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
        self.table.setColumnCount(12)  # Número de colunas ajustado para incluir novos campos
        self.table.setHorizontalHeaderLabels([
            "NOME", "IDADE", "TELEFONE", "TELEFONE EXTRA", "CIDADE", "ESCOLARIDADE", 
            "CARGO", "ANOS EXP.", "MESES EXP.", "CTPS", "VAGA ENCAMINHADA", "AÇÕES"
        ])
        self.table.setShowGrid(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Total de resultados e paginação
        pagination_layout = QHBoxLayout()
        self.previous_button = QPushButton("<< Anterior")
        self.previous_button.clicked.connect(self.previous_page)
        self.previous_button.setEnabled(False)
        pagination_layout.addWidget(self.previous_button)

        self.page_label = QLabel("Página 1")
        pagination_layout.addWidget(self.page_label, alignment=Qt.AlignCenter)

        self.next_button = QPushButton("Próximo >>")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)
        pagination_layout.addWidget(self.next_button)

        layout.addLayout(pagination_layout)

        # Total de resultados
        self.total_label = QLabel("TOTAL DE CURRÍCULOS: 0")
        self.total_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.total_label)

        self.setLayout(layout)

    def create_filter_layout(self):
        filter_layout = QGridLayout()

        # Coluna 1: CPF, NOME, SEXO, CIDADE
        filter_layout.addWidget(QLabel("CPF:"), 0, 0)
        self.cpf_input = QLineEdit()
        self.cpf_input.setPlaceholderText("Digite o CPF")
        filter_layout.addWidget(self.cpf_input, 0, 1)

        filter_layout.addWidget(QLabel("NOME:"), 1, 0)
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Digite o nome")
        filter_layout.addWidget(self.nome_input, 1, 1)

        filter_layout.addWidget(QLabel("SEXO:"), 2, 0)
        self.sexo_input = QComboBox()
        self.sexo_input.addItems(["", "MASCULINO", "FEMININO"])
        filter_layout.addWidget(self.sexo_input, 2, 1)

        filter_layout.addWidget(QLabel("CIDADE:"), 3, 0)
        self.cidade_input = QComboBox()
        self.cidade_input.addItem("")
        cidades = self.curriculo_model.listar_cidades()
        self.cidade_input.addItems(cidades)
        filter_layout.addWidget(self.cidade_input, 3, 1)

        # Divisor vertical após coluna 1
        vertical_divider1 = QFrame()
        vertical_divider1.setFrameShape(QFrame.VLine)
        vertical_divider1.setFrameShadow(QFrame.Sunken)
        vertical_divider1.setStyleSheet("background-color: #0056A1; width: 2px;")
        filter_layout.addWidget(vertical_divider1, 0, 2, 4, 1)  # Ocupa 4 linhas e 1 coluna

        # Coluna 2: IDADE MIN, IDADE MAX, TELEFONE, TELEFONE EXTRA
        filter_layout.addWidget(QLabel("IDADE MÍNIMA:"), 0, 3)
        self.idade_min_input = QSpinBox()
        self.idade_min_input.setRange(0, 120)
        self.idade_min_input.setSuffix(" anos")
        filter_layout.addWidget(self.idade_min_input, 0, 4)

        filter_layout.addWidget(QLabel("IDADE MÁXIMA:"), 1, 3)
        self.idade_max_input = QSpinBox()
        self.idade_max_input.setRange(0, 120)
        self.idade_max_input.setSuffix(" anos")
        filter_layout.addWidget(self.idade_max_input, 1, 4)

        filter_layout.addWidget(QLabel("TELEFONE:"), 2, 3)
        self.telefone_input = QLineEdit()
        self.telefone_input.setPlaceholderText("Digite o telefone")
        filter_layout.addWidget(self.telefone_input, 2, 4)

        filter_layout.addWidget(QLabel("TELEFONE EXTRA:"), 3, 3)
        self.telefone_extra_input = QLineEdit()
        self.telefone_extra_input.setPlaceholderText("Digite o telefone extra")
        filter_layout.addWidget(self.telefone_extra_input, 3, 4)

        # Divisor vertical após coluna 2
        vertical_divider2 = QFrame()
        vertical_divider2.setFrameShape(QFrame.VLine)
        vertical_divider2.setFrameShadow(QFrame.Sunken)
        vertical_divider2.setStyleSheet("background-color: #0056A1; width: 2px;")
        filter_layout.addWidget(vertical_divider2, 0, 5, 4, 1)  # Ocupa 4 linhas e 1 coluna

        # Coluna 3: ESCOLARIDADE, CARGO, SERVIÇO, VAGA ENCAMINHADA
        filter_layout.addWidget(QLabel("ESCOLARIDADE:"), 0, 6)
        self.escolaridade_input = QComboBox()
        self.escolaridade_input.addItems([
            "",
            "ENSINO FUNDAMENTAL INCOMPLETO",
            "ENSINO FUNDAMENTAL COMPLETO",
            "ENSINO MÉDIO INCOMPLETO",
            "ENSINO MÉDIO COMPLETO",
            "ENSINO SUPERIOR INCOMPLETO",
            "ENSINO SUPERIOR COMPLETO",
            "PÓS-GRADUAÇÃO/MBA",
            "MESTRADO",
            "DOUTORADO"
        ])
        filter_layout.addWidget(self.escolaridade_input, 0, 7)

        filter_layout.addWidget(QLabel("CARGO:"), 1, 6)
        self.cargo_input = QLineEdit()
        self.cargo_input.setPlaceholderText("Digite o cargo")
        filter_layout.addWidget(self.cargo_input, 1, 7)

        filter_layout.addWidget(QLabel("SERVIÇO:"), 2, 6)
        self.servico_input = QComboBox()
        self.servico_input.addItems(["", "SINE", "MANUAL"])
        filter_layout.addWidget(self.servico_input, 2, 7)

        filter_layout.addWidget(QLabel("VAGA ENCAMINHADA:"), 3, 6)
        self.vaga_encaminhada_input = QComboBox()
        self.vaga_encaminhada_input.addItems(["", "Sim", "Não"])
        filter_layout.addWidget(self.vaga_encaminhada_input, 3, 7)

        # Divisor vertical após coluna 3
        vertical_divider3 = QFrame()
        vertical_divider3.setFrameShape(QFrame.VLine)
        vertical_divider3.setFrameShadow(QFrame.Sunken)
        vertical_divider3.setStyleSheet("background-color: #0056A1; width: 2px;")
        filter_layout.addWidget(vertical_divider3, 0, 8, 4, 1)  # Ocupa 4 linhas e 1 coluna

        # Coluna 4: EXPERIÊNCIA MESES MIN, MESES MAX, ANOS MIN, ANOS MAX
        filter_layout.addWidget(QLabel("EXPERIÊNCIA (MESES MÍN.):"), 0, 9)
        self.experiencia_meses_min = QSpinBox()
        self.experiencia_meses_min.setRange(0, 11)
        filter_layout.addWidget(self.experiencia_meses_min, 0, 10)

        filter_layout.addWidget(QLabel("EXPERIÊNCIA (MESES MÁX.):"), 1, 9)
        self.experiencia_meses_max = QSpinBox()
        self.experiencia_meses_max.setRange(0, 11)
        filter_layout.addWidget(self.experiencia_meses_max, 1, 10)

        filter_layout.addWidget(QLabel("EXPERIÊNCIA (ANOS MÍN.):"), 2, 9)
        self.experiencia_anos_min = QSpinBox()
        self.experiencia_anos_min.setRange(0, 50)
        filter_layout.addWidget(self.experiencia_anos_min, 2, 10)

        filter_layout.addWidget(QLabel("EXPERIÊNCIA (ANOS MÁX.):"), 3, 9)
        self.experiencia_anos_max = QSpinBox()
        self.experiencia_anos_max.setRange(0, 50)
        filter_layout.addWidget(self.experiencia_anos_max, 3, 10)

        # Adicionar divisor horizontal
        horizontal_divider = QFrame()
        horizontal_divider.setFrameShape(QFrame.HLine)
        horizontal_divider.setFrameShadow(QFrame.Sunken)
        horizontal_divider.setStyleSheet("background-color: #0056A1; height: 2px;")
        filter_layout.addWidget(horizontal_divider, 4, 0, 1, 11)

        # Linha de botões de ação
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)  # Centraliza os botões

        # Dimensões dos botões (20% da largura da tela)
        screen_width = self.screen().geometry().width()
        button_width = int(screen_width * 0.1)

        self.search_button = QPushButton("BUSCAR")
        self.search_button.setStyleSheet(self._button_stylesheet())
        self.search_button.setFixedSize(button_width, 40)  # Largura dinâmica e altura fixa
        self.search_button.clicked.connect(self.search_curriculos)
        button_layout.addWidget(self.search_button)

        self.clear_button = QPushButton("LIMPAR FILTROS")
        self.clear_button.setStyleSheet(self._button_stylesheet())
        self.clear_button.setFixedSize(button_width, 40)  # Largura dinâmica e altura fixa
        self.clear_button.clicked.connect(self.clear_filters)
        button_layout.addWidget(self.clear_button)

        filter_layout.addLayout(button_layout, 5, 0, 1, 11)  # Adiciona os botões centralizados


        return filter_layout

    def _button_stylesheet(self):
        return """
            QPushButton {
                text-align: center;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                color: white;
                border: none;
                background-color: #026bc7;
                outline: none;
            }
            QPushButton:hover {
                background-color: #367dba;
            }
            QPushButton:pressed {
                background-color: #0056A1;
            }
        """

    def search_curriculos(self):
        filtros = {
            "nome": self.nome_input.text().strip() or None,
            "cpf": self.cpf_input.text().strip() or None,
            "sexo": self.sexo_input.currentText() or None,
            "cidade": self.cidade_input.currentText() or None,
            "idade_min": self.idade_min_input.value(),
            "idade_max": self.idade_max_input.value(),
            "escolaridade": self.escolaridade_input.currentText() or None,
            "anos_experiencia_min": self.experiencia_anos_min.value(),
            "anos_experiencia_max": self.experiencia_anos_max.value(),
            "meses_experiencia_min": self.experiencia_meses_min.value(),
            "meses_experiencia_max": self.experiencia_meses_max.value(),
            "telefone_extra": self.telefone_extra_input.text().strip() or None,
            "servico": self.servico_input.currentText() or None,
            "vaga_encaminhada": self.vaga_encaminhada_input.currentText(),
        }

        # Conversão de vaga encaminhada para booleano
        filtros["vaga_encaminhada"] = {
            "Sim": True,
            "Não": False
        }.get(filtros["vaga_encaminhada"], None)

        # Ajustar valores de idade para None se forem o padrão
        if filtros["idade_min"] == 0:
            filtros["idade_min"] = None
        if filtros["idade_max"] == 0:
            filtros["idade_max"] = None

        try:
            # Consultar total de resultados sem paginação
            self.total_results = len(self.curriculo_model.fetch_curriculos(filtros, limite=None, offset=None))

            # Buscar os resultados da página atual
            results = self.curriculo_model.fetch_curriculos(
                filtros,
                limite=self.items_per_page,
                offset=self.current_page * self.items_per_page
            )

            # Atualizar a tabela com os resultados
            self.populate_table(results)

            # Atualizar controles de paginação
            self.update_pagination_controls()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao buscar currículos: {str(e)}")

    def populate_table(self, results):
        """
        Preenche a tabela com os resultados da consulta.
        """
        self.table.setRowCount(len(results))
        for row_idx, row in enumerate(results):
            for col_idx, key in enumerate([
                "nome", "idade", "telefone", "telefone_extra", "cidade", "escolaridade", 
                "cargo", "anos_experiencia", "meses_experiencia", "tem_ctps", "vaga_encaminhada"
            ]):
                value = "Sim" if key in ("tem_ctps", "vaga_encaminhada") and row.get(key) else row.get(key, "")
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

            # Botão de edição
            edit_button = QPushButton("EDITAR")
            edit_button.clicked.connect(lambda _, id=row["curriculo_id"]: self.open_edit_dialog(id))
            self.table.setCellWidget(row_idx, 11, edit_button)

        self.total_label.setText(f"TOTAL DE CURRÍCULOS: {self.total_results}")

    def update_pagination_controls(self):
        """
        Atualiza os botões de paginação e o rótulo de página.
        """
        total_pages = -(-self.total_results // self.items_per_page)  # Arredondar para cima
        self.page_label.setText(f"Página {self.current_page + 1} de {total_pages}")

        self.previous_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total_pages - 1)

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.search_curriculos()

    def next_page(self):
        total_pages = -(-self.total_results // self.items_per_page)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.search_curriculos()

    def open_edit_dialog(self, curriculo_id):
        """
        Abre a caixa de diálogo para editar o currículo.
        """
        curriculo = self.curriculo_model.get_curriculo_by_id(curriculo_id)
        if not curriculo:
            QMessageBox.critical(self, "Erro", f"ERRO AO CARREGAR DADOS: Currículo não encontrado.")
            return

        dialog = EditDialog(self.curriculo_model, curriculo_id, self)
        if dialog.exec():
            self.search_curriculos()

    def clear_filters(self):
        self.nome_input.clear()
        self.cpf_input.clear()
        self.sexo_input.setCurrentIndex(0)
        self.cidade_input.setCurrentIndex(0)
        self.escolaridade_input.setCurrentIndex(0)
        self.experiencia_anos_min.setValue(0)
        self.experiencia_anos_max.setValue(0)
        self.experiencia_meses_min.setValue(0)
        self.experiencia_meses_max.setValue(0)
        self.telefone_extra_input.clear()
        self.servico_input.setCurrentIndex(0)
        self.vaga_encaminhada_input.setCurrentIndex(0)
        self.search_curriculos()