from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QGridLayout, QFrame, 
    QTableWidget, QTableWidgetItem, QComboBox, QSpinBox, QMessageBox, QGroupBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
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

        # Layout horizontal para os botões de ação (Buscar e Limpar)
        button_layout = QHBoxLayout()

        # Centraliza os botões no layout
        button_layout.setAlignment(Qt.AlignCenter)

        self.search_button = QPushButton("Buscar")
        self.search_button.setIcon(QIcon("assets/icons/search-icon.svg"))
        self.search_button.setStyleSheet(self._button_stylesheet())
        self.search_button.clicked.connect(self.search_curriculos)
        button_layout.addWidget(self.search_button)

        self.clear_button = QPushButton("Limpar Filtros")
        self.clear_button.setIcon(QIcon("assets/icons/clear-icon.svg"))
        self.clear_button.setStyleSheet(self._button_stylesheet())
        self.clear_button.clicked.connect(self.clear_filters)
        button_layout.addWidget(self.clear_button)

        # Adiciona o layout de botões ao layout principal
        layout.addLayout(button_layout)

        # Tabela de resultados
        self.table = QTableWidget()
        self.table.setColumnCount(14)  # Número de colunas ajustado para incluir novos campos
        self.table.setHorizontalHeaderLabels([
            "NOME", "IDADE", "TELEFONE", "TELEFONE EXTRA", "CIDADE", "ESCOLARIDADE",
            "CARGO", "ANOS EXP.", "MESES EXP.", "CTPS", "VAGA ENCAMINHADA", 
            "PRIMEIRO EMPREGO", "CEP", "AÇÕES"  # Novos campos adicionados
        ])
        self.table.setShowGrid(True)
        header = self.table.horizontalHeader()
        # Define a primeira coluna para preencher o espaço restante
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        # Define as demais colunas para se ajustarem ao conteúdo
        for col in range(1, self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

        # Layout para total de currículos e paginação
        bottom_layout = QVBoxLayout()

        # Total de currículos (centralizado)
        self.total_label = QLabel("TOTAL DE CURRÍCULOS: 0")
        self.total_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        total_layout = QHBoxLayout()
        total_layout.addWidget(self.total_label, alignment=Qt.AlignCenter)

        # Adiciona "TOTAL DE CURRÍCULOS" ao layout
        bottom_layout.addLayout(total_layout)

        # Layout para os botões de paginação
        pagination_layout = QHBoxLayout()

        # Botões de paginação nas extremidades
        self.previous_button = QPushButton("<< Anterior")
        self.previous_button.setStyleSheet(self._button_stylesheet())  # Aplica o mesmo estilo
        self.previous_button.setMinimumWidth(100)  # Mesmo tamanho do botão "Buscar"
        self.previous_button.setFixedHeight(36)  # Mesmo tamanho do botão "Buscar"
        self.previous_button.clicked.connect(self.previous_page)
        self.previous_button.setEnabled(False)
        pagination_layout.addWidget(self.previous_button, alignment=Qt.AlignLeft)

        self.page_label = QLabel("Página 1")
        pagination_layout.addWidget(self.page_label, alignment=Qt.AlignCenter)

        self.next_button = QPushButton("Próximo >>")
        self.next_button.setStyleSheet(self._button_stylesheet())  # Aplica o mesmo estilo
        self.next_button.setMinimumWidth(100)  # Mesmo tamanho do botão "Buscar"
        self.next_button.setFixedHeight(36)  # Mesmo tamanho do botão "Buscar"
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)
        pagination_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

        # Adiciona os botões de paginação ao layout
        bottom_layout.addLayout(pagination_layout)

        # Adiciona o layout final ao layout principal
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    def create_filter_layout(self):
        filter_layout = QGridLayout()

        # **Primeira coluna (CPF, NOME, SEXO, IDADE MÍNIMA, IDADE MÁXIMA)**
        filter_layout.addWidget(QLabel("CPF:"), 0, 0)
        self.cpf_input = QLineEdit()
        self.cpf_input.setPlaceholderText("Digite o CPF")
        self.cpf_input.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.cpf_input, 0, 1)

        filter_layout.addWidget(QLabel("NOME:"), 1, 0)
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Digite o nome")
        self.nome_input.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.nome_input, 1, 1)

        filter_layout.addWidget(QLabel("SEXO:"), 2, 0)
        self.sexo_input = QComboBox()
        self.sexo_input.setEditable(True)
        self.sexo_input.addItems(["", "MASCULINO", "FEMININO"])
        self.sexo_input.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.sexo_input, 2, 1)

        filter_layout.addWidget(QLabel("IDADE MÍNIMA:"), 3, 0)
        self.idade_min_input = QSpinBox()
        self.idade_min_input.setRange(0, 120)
        self.idade_min_input.setSuffix(" anos")
        self.idade_min_input.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.idade_min_input, 3, 1)

        filter_layout.addWidget(QLabel("IDADE MÁXIMA:"), 4, 0)
        self.idade_max_input = QSpinBox()
        self.idade_max_input.setRange(0, 120)
        self.idade_max_input.setSuffix(" anos")
        self.idade_max_input.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.idade_max_input, 4, 1)

        # **Segunda coluna (CEP, CIDADE, TELEFONE, TELEFONE EXTRA, ESCOLARIDADE)**
        filter_layout.addWidget(QLabel("CEP:"), 0, 2)
        self.cep_input = QLineEdit()
        self.cep_input.setPlaceholderText("Digite o CEP")
        self.cep_input.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.cep_input, 0, 3)

        filter_layout.addWidget(QLabel("CIDADE:"), 1, 2)
        self.cidade_input = QComboBox()
        self.cidade_input.setEditable(True)
        self.cidade_input.addItem("")
        cidades = self.curriculo_model.listar_cidades()
        self.cidade_input.addItems(cidades)
        self.cidade_input.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.cidade_input, 1, 3)

        filter_layout.addWidget(QLabel("TELEFONE:"), 2, 2)
        self.telefone_input = QLineEdit()
        self.telefone_input.setPlaceholderText("Digite o telefone")
        self.telefone_input.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.telefone_input, 2, 3)

        filter_layout.addWidget(QLabel("TELEFONE EXTRA:"), 3, 2)
        self.telefone_extra_input = QLineEdit()
        self.telefone_extra_input.setPlaceholderText("Digite o telefone extra")
        self.telefone_extra_input.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.telefone_extra_input, 3, 3)

        filter_layout.addWidget(QLabel("ESCOLARIDADE:"), 4, 2)
        self.escolaridade_input = QComboBox()
        self.escolaridade_input.setEditable(True)
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
        self.escolaridade_input.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.escolaridade_input, 4, 3)

        # **Terceira coluna (CARGO, SERVIÇO, VAGA ENCAMINHADA, PRIMEIRO EMPREGO)**
        filter_layout.addWidget(QLabel("CARGO:"), 0, 4)
        self.cargo_input = QLineEdit()
        self.cargo_input.setPlaceholderText("Digite o cargo")
        self.cargo_input.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.cargo_input, 0, 5)

        filter_layout.addWidget(QLabel("SERVIÇO:"), 1, 4)
        self.servico_input = QComboBox()
        self.servico_input.setEditable(True)
        self.servico_input.addItems(["", "SINE", "MANUAL"])
        self.servico_input.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.servico_input, 1, 5)

        filter_layout.addWidget(QLabel("VAGA ENCAMINHADA:"), 2, 4)
        self.vaga_encaminhada_input = QComboBox()
        self.vaga_encaminhada_input.setEditable(True)
        self.vaga_encaminhada_input.addItems(["", "Sim", "Não"])
        self.vaga_encaminhada_input.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.vaga_encaminhada_input, 2, 5)

        filter_layout.addWidget(QLabel("PRIMEIRO EMPREGO:"), 3, 4)
        self.primeiro_emprego_input = QComboBox()
        self.primeiro_emprego_input.setEditable(True)
        self.primeiro_emprego_input.addItems(["", "Sim", "Não"])
        self.primeiro_emprego_input.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.primeiro_emprego_input, 3, 5)

        # **Quarta coluna (EXPERIÊNCIA ANOS MIN, ANOS MAX, MESES MIN, MESES MAX, CTPS)**
        filter_layout.addWidget(QLabel("EXPERIÊNCIA (ANOS MÍN.):"), 0, 6)
        self.experiencia_anos_min = QSpinBox()
        self.experiencia_anos_min.setRange(0, 50)
        self.experiencia_anos_min.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.experiencia_anos_min, 0, 7)

        filter_layout.addWidget(QLabel("EXPERIÊNCIA (ANOS MÁX.):"), 1, 6)
        self.experiencia_anos_max = QSpinBox()
        self.experiencia_anos_max.setRange(0, 50)
        self.experiencia_anos_max.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.experiencia_anos_max, 1, 7)

        filter_layout.addWidget(QLabel("EXPERIÊNCIA (MESES MÍN.):"), 2, 6)
        self.experiencia_meses_min = QSpinBox()
        self.experiencia_meses_min.setRange(0, 11)  # Meses variam de 0 a 11
        self.experiencia_meses_min.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.experiencia_meses_min, 2, 7)

        filter_layout.addWidget(QLabel("EXPERIÊNCIA (MESES MÁX.):"), 3, 6)
        self.experiencia_meses_max = QSpinBox()
        self.experiencia_meses_max.setRange(0, 11)
        self.experiencia_meses_max.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.experiencia_meses_max, 3, 7)

        filter_layout.addWidget(QLabel("CTPS:"), 4, 6)
        self.ctps_input = QComboBox()
        self.ctps_input.setEditable(True)
        self.ctps_input.addItems(["", "Sim", "Não"])
        self.ctps_input.setFixedHeight(25)  # Reduzindo a altura
        filter_layout.addWidget(self.ctps_input, 4, 7)

        return filter_layout

    def _button_stylesheet(self):
        return """
            QPushButton {
                text-align: center;
                border-radius: 10px;  /* Bordas mais arredondadas */
                font-size: 14px;  /* Texto menor */
                font-weight: bold;
                color: white;
                border: 2px solid #026bc7;  /* Cor da borda */
                background-color: #026bc7;
                padding: 8px 12px;  /* Botão menor, com menos espaçamento interno */
                outline: none;
                width: 100px;  /* Largura fixa para os botões */
                min-width: 120px;  /* Largura mínima do botão */
                max-width: 160px;  /* Máxima largura para os botões, se necessário */
            }
            QPushButton:hover {
                background-color: #367dba;
            }
            QPushButton:pressed {
                background-color: #0056A1;
            }
        """
    
    def search_curriculos(self):
        # Calcula a experiência mínima e máxima em meses
        experiencia_min_meses = (self.experiencia_anos_min.value() * 12) + self.experiencia_meses_min.value()
        experiencia_max_meses = (self.experiencia_anos_max.value() * 12) + self.experiencia_meses_max.value()

        # Define os filtros com as variáveis calculadas
        filtros = {
            "nome": self.nome_input.text().strip() or None,
            "cpf": self.cpf_input.text().strip() or None,
            "sexo": self.sexo_input.currentText() or None,
            "cidade": self.cidade_input.currentText() or None,
            "idade_min": self.idade_min_input.value() or None,
            "idade_max": self.idade_max_input.value() or None,
            "escolaridade": self.escolaridade_input.currentText() or None,
            "telefone": self.telefone_input.text().strip() or None,
            "telefone_extra": self.telefone_extra_input.text().strip() or None,
            "servico": self.servico_input.currentText() or None,
            "vaga_encaminhada": {
                "Sim": True,
                "Não": False
            }.get(self.vaga_encaminhada_input.currentText(), None),
            "primeiro_emprego": {
                "Sim": True,
                "Não": False
            }.get(self.primeiro_emprego_input.currentText(), None),
            "cep": self.cep_input.text().strip() or None,
            "tem_ctps": {
                "Sim": True,
                "Não": False
            }.get(self.ctps_input.currentText(), None),
            "cargo": self.cargo_input.text().strip() or None,  # Filtro de cargo adicionado
            "experiencia_min": experiencia_min_meses if experiencia_min_meses > 0 else None,
            "experiencia_max": experiencia_max_meses if experiencia_max_meses > 0 else None,
        }

        try:
            # Consulta o banco para obter resultados e popular a tabela
            self.total_results = len(self.curriculo_model.fetch_curriculos(filtros, limite=None, offset=None))
            results = self.curriculo_model.fetch_curriculos(
                filtros,
                limite=self.items_per_page,
                offset=self.current_page * self.items_per_page
            )
            self.populate_table(results)
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
                "cargo", "anos_experiencia", "meses_experiencia", "tem_ctps", "vaga_encaminhada", 
                "primeiro_emprego", "cep"  # Novas colunas adicionadas
            ]):
                # Para valores booleanos, exibe "Sim" ou "Não"
                if key in ("tem_ctps", "vaga_encaminhada", "primeiro_emprego"):
                    value = "Sim" if row.get(key) else "Não"
                else:
                    value = row.get(key, "")

                # Preenche o valor na célula
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

            # Botão de edição
            edit_button = QPushButton("EDITAR")
            edit_button.clicked.connect(lambda _, id=row["curriculo_id"]: self.open_edit_dialog(id))
            self.table.setCellWidget(row_idx, 13, edit_button)  # Ajustado para a nova última coluna

        # Atualiza o total de resultados exibido
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
        """
        Limpa todos os filtros e redefine para os valores padrão.
        """
        self.nome_input.clear()
        self.cpf_input.clear()
        self.sexo_input.setCurrentIndex(0)
        self.cidade_input.setCurrentIndex(0)
        self.escolaridade_input.setCurrentIndex(0)
        self.experiencia_anos_min.setValue(0)
        self.experiencia_anos_max.setValue(0)
        self.experiencia_meses_min.setValue(0)
        self.experiencia_meses_max.setValue(0)
        self.telefone_input.clear()
        self.telefone_extra_input.clear()
        self.servico_input.setCurrentIndex(0)
        self.vaga_encaminhada_input.setCurrentIndex(0)
        self.idade_min_input.setValue(0)  # Resetar filtro de idade mínima
        self.idade_max_input.setValue(0)  # Resetar filtro de idade máxima
        self.primeiro_emprego_input.setCurrentIndex(0)  # Limpar filtro de primeiro emprego
        self.cep_input.clear()  # Limpar filtro de CEP
        self.cargo_input.clear()  # Limpar filtro de cargo
        self.ctps_input.setCurrentIndex(0)  # Limpar filtro de CTPS

        self.search_curriculos()
