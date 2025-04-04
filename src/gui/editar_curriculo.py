import datetime
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QComboBox, QMessageBox, QPushButton, QDateEdit
from PySide6.QtCore import Qt, QDate, QEvent
from models.curriculo_model import CurriculoModel
from PySide6.QtGui import QKeyEvent  # Import necessário

class EditDialog(QDialog):
    def __init__(self, curriculo_model, curriculo_id, parent=None):
        super().__init__(parent)
        self.curriculo_model = curriculo_model
        self.curriculo_id = curriculo_id

        self.setWindowTitle("EDITAR CURRÍCULO")
        self.setup_ui()
        self.load_cidades()  # Carregar as cidades
        self.load_curriculo_data()

    def setup_ui(self):
        self.setLayout(QVBoxLayout())

        # Campos para edição
        self.nome_input = QLineEdit()
        self.cpf_input = QLineEdit()
        self.sexo_input = QComboBox()
        self.sexo_input.addItems(["MASCULINO", "FEMININO"])
        self.sexo_input.setEditable(True)  # Torna o combo box editável
        self.data_nascimento_input = QDateEdit(calendarPopup=True)
        self.data_nascimento_input.setDisplayFormat("dd/MM/yyyy")
        self.telefone_input = QLineEdit()
        self.telefone_extra_input = QLineEdit()
        self.cidade_input = QComboBox()
        self.cidade_input.setEditable(True)  # Torna o combo box editável
        self.escolaridade_input = QComboBox()
        self.escolaridade_input.addItems(["", "ENSINO FUNDAMENTAL INCOMPLETO", "ENSINO FUNDAMENTAL COMPLETO", 
                                        "ENSINO MÉDIO INCOMPLETO", "ENSINO MÉDIO COMPLETO", 
                                        "ENSINO SUPERIOR INCOMPLETO", "ENSINO SUPERIOR COMPLETO", 
                                        "PÓS-GRADUAÇÃO/MBA", "MESTRADO", "DOUTORADO"])
        self.escolaridade_input.setEditable(True)  # Torna o combo box editável
        self.tem_ctps_input = QComboBox()
        self.tem_ctps_input.addItems(["SIM", "NÃO"])
        self.tem_ctps_input.setEditable(True)  # Torna o combo box editável
        self.funcao_input = QLineEdit()
        self.anos_experiencia_input = QSpinBox()
        self.anos_experiencia_input.setRange(0, 50)
        self.meses_experiencia_input = QSpinBox()
        self.meses_experiencia_input.setRange(0, 11)
        self.cep_input = QLineEdit()
        self.pcd_input = QComboBox()
        self.pcd_input.addItems(["SIM", "NÃO"])


        # Adicionando campos à interface
        fields = [
            ("NOME", self.nome_input),
            ("CPF", self.cpf_input),
            ("SEXO", self.sexo_input),
            ("DATA DE NASCIMENTO", self.data_nascimento_input),
            ("TELEFONE", self.telefone_input),
            ("TELEFONE EXTRA", self.telefone_extra_input),
            ("CIDADE", self.cidade_input),
            ("ESCOLARIDADE", self.escolaridade_input),
            ("TEM CTPS", self.tem_ctps_input),
            ("FUNÇÃO", self.funcao_input),
            ("ANOS DE EXPERIÊNCIA", self.anos_experiencia_input),
            ("MESES DE EXPERIÊNCIA", self.meses_experiencia_input),
            ("CEP", self.cep_input),
            ("PCD", self.pcd_input)
        ]

        for label, widget in fields:
            self.layout().addWidget(QLabel(label))
            self.layout().addWidget(widget)

        # Botões
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("SALVAR")
        self.save_button.clicked.connect(self.save_changes)
        self.cancel_button = QPushButton("CANCELAR")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        self.layout().addLayout(button_layout)

        # Configurar navegação com Enter
        self.configurar_transicao_enter([widget for _, widget in fields] + [self.save_button])

    def load_cidades(self):
        """
        Carrega as cidades do banco de dados e adiciona no QComboBox.
        """
        try:
            cidades = self.curriculo_model.listar_cidades()  # Busca cidades do banco
            if cidades:
                self.cidade_input.addItems(cidades)
            else:
                QMessageBox.warning(self, "AVISO", "NÃO HÁ CIDADES CADASTRADAS.")
        except Exception as e:
            QMessageBox.critical(self, "ERRO", f"ERRO AO CARREGAR CIDADES: {e}")

    def load_curriculo_data(self):
        """
        Carrega os dados do currículo do banco de dados.
        """
        try:
            curriculo = self.curriculo_model.get_curriculo_by_id(self.curriculo_id)
            experiencias = self.curriculo_model.fetch_experiencias(self.curriculo_id)

            if curriculo:
                self.nome_input.setText(curriculo.get("nome", ""))
                self.cpf_input.setText(curriculo.get("cpf", ""))
                self.sexo_input.setCurrentText(curriculo.get("sexo", ""))

                # Tratamento da data de nascimento
                data_nascimento_str = curriculo.get("data_nascimento", "")
                if data_nascimento_str:
                    # Se data_nascimento_str é um objeto datetime.date, converta para string
                    if isinstance(data_nascimento_str, datetime.date):
                        data_nascimento_str = data_nascimento_str.strftime("%Y-%m-%d")  # Formato "yyyy-MM-dd"
                    
                    # Agora use a string no formato correto com QDate.fromString
                    date = QDate.fromString(data_nascimento_str, "yyyy-MM-dd")
                    if date.isValid():
                        self.data_nascimento_input.setDate(date)
                    else:
                        self.data_nascimento_input.clear()  # Limpa o campo se a data não for válida
                else:
                    self.data_nascimento_input.clear()

                self.telefone_input.setText(curriculo.get("telefone", ""))
                self.telefone_extra_input.setText(curriculo.get("telefone_extra", ""))
                self.cidade_input.setCurrentText(curriculo.get("cidade", ""))
                self.escolaridade_input.setCurrentText(curriculo.get("escolaridade", ""))
                self.tem_ctps_input.setCurrentText("SIM" if curriculo.get("tem_ctps") else "NÃO")
                self.cep_input.setText(curriculo.get("cep", ""))

                if experiencias:
                    self.funcao_input.setText(experiencias[0].get("funcao", ""))
                    self.anos_experiencia_input.setValue(experiencias[0].get("anos_experiencia", 0))
                    self.meses_experiencia_input.setValue(experiencias[0].get("meses_experiencia", 0))
            else:
                QMessageBox.warning(self, "AVISO", "CURRÍCULO NÃO ENCONTRADO.")
                self.reject()
        except Exception as e:
            QMessageBox.critical(self, "ERRO", f"ERRO AO CARREGAR DADOS: {e}")
            self.reject()

    def configurar_transicao_enter(self, widgets):
        """Configura a navegação entre widgets usando Enter."""
        for widget in widgets:
            widget.installEventFilter(self)

    def eventFilter(self, source, event):
        """Captura o evento Enter para alternar entre widgets e acionar o botão."""
        if event.type() == QEvent.KeyPress and event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Lista de widgets para o cadastro
            fields = [
                self.nome_input, self.cpf_input, self.sexo_input, self.data_nascimento_input,
                self.telefone_input, self.telefone_extra_input, self.cidade_input,
                self.escolaridade_input, self.tem_ctps_input,
                self.funcao_input, self.anos_experiencia_input,
                self.meses_experiencia_input, self.cep_input, self.pcd_input
            ]

            # Verifica a navegação nos campos
            if source in fields:
                current_index = fields.index(source)
                next_index = current_index + 1
                if next_index < len(fields):
                    fields[next_index].setFocus()
                else:
                    self.save_button.click()  # Aciona o botão Salvar
                return True  # Evento tratado

        return super().eventFilter(source, event)

    def save_changes(self):
        """
        Salva as alterações no banco de dados com os novos campos.
        """
        nome = self.nome_input.text().strip()
        cpf = self.cpf_input.text().strip()
        sexo = self.sexo_input.currentText()
        data_nascimento = self.data_nascimento_input.date().toString("yyyy-MM-dd")
        telefone = self.telefone_input.text().strip()
        telefone_extra = self.telefone_extra_input.text().strip()
        cidade = self.cidade_input.currentText()
        escolaridade = self.escolaridade_input.currentText()
        tem_ctps = self.tem_ctps_input.currentText() == "SIM"
        pcd = self.pcd_input.currentText() == "SIM"  # Novo campo PCD
        cep = self.cep_input.text().strip()

        # Validação básica
        if not nome or not cpf or not telefone or not cidade:
            QMessageBox.warning(self, "AVISO", "CAMPOS OBRIGATÓRIOS: NOME, CPF, TELEFONE E CIDADE.")
            return

        try:
            # Obtém ID da cidade
            cidade_id = self.curriculo_model.obter_cidade_id(cidade)
            if not cidade_id:
                raise ValueError("CIDADE NÃO ENCONTRADA")

            # Atualiza currículo
            self.curriculo_model.update_curriculo(
                self.curriculo_id, 
                nome, 
                cpf, 
                sexo, 
                data_nascimento, 
                cidade_id,
                telefone,
                telefone_extra,
                escolaridade,
                tem_ctps,
                cep,
                pcd  # Novo parâmetro PCD
            )

            QMessageBox.information(self, "SUCESSO", "CURRÍCULO ATUALIZADO!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "ERRO", f"FALHA AO SALVAR: {str(e)}")