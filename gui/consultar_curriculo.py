from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QGridLayout,
    QTableWidget, QTableWidgetItem, QComboBox, QSpinBox, QMessageBox, QScrollArea, QFileDialog, QSpacerItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHeaderView
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from models.curriculo_model import CurriculoModel
from gui.editar_curriculo import EditDialog
from gui.busca_cep import consultar_cep

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

        # Botões de busca e limpeza
        button_layout = QHBoxLayout()
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

        button_layout.addStretch()

        self.generate_pdf_button = QPushButton("Gerar Relatório")
        self.generate_pdf_button.setIcon(QIcon("assets/icons/pdf-icon.svg"))
        self.generate_pdf_button.setStyleSheet(self._button_stylesheet())
        self.generate_pdf_button.clicked.connect(self.generate_pdf_report)
        button_layout.addWidget(self.generate_pdf_button)

        layout.addLayout(button_layout)

        # Criando área de rolagem para a tabela
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)

        # Tabela de resultados
        self.table = QTableWidget()
        self.table.setColumnCount(14)
        self.table.setHorizontalHeaderLabels([ 
            "CPF", "NOME", "IDADE", "TELEFONE", "TELEFONE EXTRA", "CEP", 
            "CIDADE", "ESCOLARIDADE", "FUNÇÃO", "ANOS EXP.", "MESES EXP.", 
            "CTPS", "PCD", "AÇÕES" 
        ])
        self.table.setShowGrid(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        for col in range(1, self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

        table_layout.addWidget(self.table)
        table_container.setLayout(table_layout)
        scroll_area.setWidget(table_container)

        layout.addWidget(scroll_area)

        # Total de currículos e paginação
        bottom_layout = QVBoxLayout()
        self.total_label = QLabel("TOTAL DE CURRÍCULOS: 0")
        self.total_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        total_layout = QHBoxLayout()
        total_layout.addWidget(self.total_label, alignment=Qt.AlignCenter)
        bottom_layout.addLayout(total_layout)

        pagination_layout = QHBoxLayout()
        self.previous_button = QPushButton("<< Anterior")
        self.previous_button.setStyleSheet(self._button_stylesheet())
        self.previous_button.setEnabled(False)
        self.previous_button.clicked.connect(self.previous_page)
        pagination_layout.addWidget(self.previous_button, alignment=Qt.AlignLeft)

        self.page_label = QLabel("Página 1")
        pagination_layout.addWidget(self.page_label, alignment=Qt.AlignCenter)

        self.next_button = QPushButton("Próximo >>")
        self.next_button.setStyleSheet(self._button_stylesheet())
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

        bottom_layout.addLayout(pagination_layout)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    def atualizar_cidade_com_cep(self):
        # Pega o texto do campo de CEP
        cep = self.cep_input.text()
        
        # Verifica se o CEP tem 8 caracteres
        if len(cep.replace("-", "")) == 8:  # Remove o hífen, se houver
            consultar_cep(self.cep_input, self.cidade_input)
        else:
            # Se o CEP não tem 8 caracteres, não faz a consulta
            self.cidade_input.clear()  # Limpa o campo de cidade

    def create_filter_layout(self):
        filter_layout = QGridLayout()

        # **Primeira coluna (SEXO, IDADE MÍNIMA, IDADE MÁXIMA)**
        filter_layout.addWidget(QLabel("SEXO:"), 0, 0)
        self.sexo_input = QComboBox()
        self.sexo_input.setEditable(True)
        self.sexo_input.addItems(["", "MASCULINO", "FEMININO"])
        self.sexo_input.setFixedHeight(30)
        filter_layout.addWidget(self.sexo_input, 0, 1)

        filter_layout.addWidget(QLabel("IDADE MÍNIMA:"), 1, 0)
        self.idade_min_input = QSpinBox()
        self.idade_min_input.setRange(0, 120)
        self.idade_min_input.setSuffix(" anos")
        self.idade_min_input.setFixedHeight(30)
        filter_layout.addWidget(self.idade_min_input, 1, 1)

        filter_layout.addWidget(QLabel("IDADE MÁXIMA:"), 2, 0)
        self.idade_max_input = QSpinBox()
        self.idade_max_input.setRange(0, 120)
        self.idade_max_input.setSuffix(" anos")
        self.idade_max_input.setFixedHeight(30)
        filter_layout.addWidget(self.idade_max_input, 2, 1)

        # **Segunda coluna (CEP, CIDADE, ESCOLARIDADE)**
        filter_layout.addWidget(QLabel("CEP:"), 0, 2)
        self.cep_input = QLineEdit()
        self.cep_input.setPlaceholderText("Digite o CEP")
        self.cep_input.setFixedHeight(30)
        filter_layout.addWidget(self.cep_input, 0, 3)

        filter_layout.addWidget(QLabel("CIDADE:"), 1, 2)
        self.cidade_input = QComboBox()
        self.cidade_input.setEditable(True)
        self.cidade_input.addItem("")
        cidades = self.curriculo_model.listar_cidades()
        self.cidade_input.addItems(cidades)
        self.cidade_input.setFixedHeight(30)
        filter_layout.addWidget(self.cidade_input, 1, 3)

        filter_layout.addWidget(QLabel("ESCOLARIDADE:"), 2, 2)
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
        self.escolaridade_input.setFixedHeight(30)
        filter_layout.addWidget(self.escolaridade_input, 2, 3)

        # **Terceira coluna (FUNÇÃO, SERVIÇO, PCD)**
        filter_layout.addWidget(QLabel("FUNÇÃO:"), 0, 4)
        self.funcao_input = QLineEdit()
        self.funcao_input.setPlaceholderText("Digite a função")
        self.funcao_input.setFixedHeight(30)
        filter_layout.addWidget(self.funcao_input, 0, 5)

        filter_layout.addWidget(QLabel("SERVIÇO:"), 1, 4)
        self.servico_input = QComboBox()
        self.servico_input.setEditable(True)
        self.servico_input.addItems(["", "SINE", "MANUAL"])
        self.servico_input.setFixedHeight(30)
        filter_layout.addWidget(self.servico_input, 1, 5)

        filter_layout.addWidget(QLabel("PCD:"), 2, 4)
        self.pcd_input = QComboBox()
        self.pcd_input.setEditable(True)
        self.pcd_input.addItems(["", "Sim", "Não"])
        self.pcd_input.setFixedHeight(30)
        filter_layout.addWidget(self.pcd_input, 2, 5)

        # **Quarta coluna (EXPERIÊNCIA, CTPS)**
        filter_layout.addWidget(QLabel("EXPERIÊNCIA (ANOS MÍN.):"), 0, 6)
        self.experiencia_anos_min = QSpinBox()
        self.experiencia_anos_min.setRange(0, 50)
        self.experiencia_anos_min.setFixedHeight(30)
        filter_layout.addWidget(self.experiencia_anos_min, 0, 7)

        filter_layout.addWidget(QLabel("EXPERIÊNCIA (ANOS MÁX.):"), 1, 6)
        self.experiencia_anos_max = QSpinBox()
        self.experiencia_anos_max.setRange(0, 50)
        self.experiencia_anos_max.setFixedHeight(30)
        filter_layout.addWidget(self.experiencia_anos_max, 1, 7)

        filter_layout.addWidget(QLabel("EXPERIÊNCIA (MESES MÍN.):"), 2, 6)
        self.experiencia_meses_min = QSpinBox()
        self.experiencia_meses_min.setRange(0, 11)
        self.experiencia_meses_min.setFixedHeight(30)
        filter_layout.addWidget(self.experiencia_meses_min, 2, 7)

        filter_layout.addWidget(QLabel("EXPERIÊNCIA (MESES MÁX.):"), 3, 6)
        self.experiencia_meses_max = QSpinBox()
        self.experiencia_meses_max.setRange(0, 11)
        self.experiencia_meses_max.setFixedHeight(30)
        filter_layout.addWidget(self.experiencia_meses_max, 3, 7)

        filter_layout.addWidget(QLabel("CTPS:"), 4, 6)
        self.ctps_input = QComboBox()
        self.ctps_input.setEditable(True)
        self.ctps_input.addItems(["", "Sim", "Não"])
        self.ctps_input.setFixedHeight(30)
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
            "sexo": self.sexo_input.currentText() or None,
            "cidade": self.cidade_input.currentText() or None,
            "idade_min": self.idade_min_input.value() or None,
            "idade_max": self.idade_max_input.value() or None,
            "escolaridade": self.escolaridade_input.currentText() or None,
            "servico": self.servico_input.currentText() or None,
            "pcd": {
                "Sim": True,
                "Não": False
            }.get(self.pcd_input.currentText(), None),
            "cep": self.cep_input.text().strip() or None,
            "tem_ctps": {
                "Sim": True,
                "Não": False
            }.get(self.ctps_input.currentText(), None),
            "funcao": self.funcao_input.text().strip() or None,
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
                "cpf", "nome", "idade", "cep", "cidade", "escolaridade", 
                "funcao", "anos_experiencia", "meses_experiencia", "tem_ctps", "pcd"
            ]):
                # Para valores booleanos, exibe "Sim" ou "Não"
                if key in ("tem_ctps", "pcd"):
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
            self.table.setCellWidget(row_idx, 12, edit_button)  # Ajustado para a nova última coluna

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
        self.sexo_input.setCurrentIndex(0)
        self.cidade_input.setCurrentIndex(0)
        self.escolaridade_input.setCurrentIndex(0)
        self.experiencia_anos_min.setValue(0)
        self.experiencia_anos_max.setValue(0)
        self.experiencia_meses_min.setValue(0)
        self.experiencia_meses_max.setValue(0)
        self.servico_input.setCurrentIndex(0)
        self.idade_min_input.setValue(0)
        self.idade_max_input.setValue(0)
        self.cep_input.clear()
        self.funcao_input.clear()
        self.ctps_input.setCurrentIndex(0)
        self.pcd_input.setCurrentIndex(0)  # Limpar filtro de PCD

        self.search_curriculos()

    def generate_pdf_report(self):
        # Captura os dados da tabela
        rows = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            rows.append(row_data)

        # Criação do arquivo PDF
        pdf_filename, _ = QFileDialog.getSaveFileName(
            self, "Salvar Relatório", "", "PDF Files (*.pdf)"
        )
        if not pdf_filename:
            return

        if not pdf_filename.endswith(".pdf"):
            pdf_filename += ".pdf"

        c = canvas.Canvas(pdf_filename, pagesize=letter)
        width, height = letter

        # Definir a posição inicial no PDF
        y_position = height - 40
        margin = 40

        # Título
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y_position, "Relatório de Currículos Consultados")
        y_position -= 20

        # Cabeçalho da tabela
        c.setFont("Helvetica-Bold", 10)
        header = [
            "CPF", "NOME", "IDADE", "TELEFONE", "TELEFONE EXTRA", "CEP",
            "CIDADE", "ESCOLARIDADE", "FUNÇÃO", "ANOS EXP.", "MESES EXP.",
            "CTPS", "PCD"
        ]
        col_widths = [50, 100, 40, 80, 80, 60, 100, 120, 100, 50, 50, 60, 50]

        for col_idx, header_text in enumerate(header):
            c.drawString(margin + sum(col_widths[:col_idx]), y_position, header_text)

        y_position -= 20

        # Dados da tabela
        c.setFont("Helvetica", 10)
        for row in rows:
            for col_idx, cell_text in enumerate(row):
                c.drawString(margin + sum(col_widths[:col_idx]), y_position, str(cell_text))
            y_position -= 15

            # Verificar se precisa de nova página
            if y_position < 40:
                c.showPage()
                c.setFont("Helvetica", 10)
                y_position = height - 40
                for col_idx, header_text in enumerate(header):
                    c.drawString(margin + sum(col_widths[:col_idx]), y_position, header_text)
                y_position -= 20

        # Salvar o PDF
        c.save()

        # Notificar o usuário
        QMessageBox.information(self, "Sucesso", "Relatório gerado com sucesso!")
