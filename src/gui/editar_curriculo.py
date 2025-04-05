import datetime
from PySide6.QtWidgets import QDialog, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QSpinBox, QComboBox, QMessageBox, QPushButton, QDateEdit
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
        layout = QGridLayout()  # Usando um grid layout agora
        self.setLayout(layout)

        # Campos para edição
        self.nome_input = QLineEdit()
        self.cpf_input = QLineEdit()
        self.sexo_input = QComboBox()
        self.sexo_input.addItems(["MASCULINO", "FEMININO"])
        self.sexo_input.setEditable(True)
        self.data_nascimento_input = QLineEdit()
        self.data_nascimento_input.setPlaceholderText("DD/MM/AAAA")
        self.data_nascimento_input.setInputMask("00/00/0000")
        self.data_nascimento_input.installEventFilter(self)
        self.telefone_input = QLineEdit()
        self.telefone_extra_input = QLineEdit()
        self.cidade_input = QComboBox()
        self.cidade_input.setEditable(True)
        self.escolaridade_input = QComboBox()
        self.escolaridade_input.addItems(["", "ENSINO FUNDAMENTAL INCOMPLETO", "ENSINO FUNDAMENTAL COMPLETO", 
                                          "ENSINO MÉDIO INCOMPLETO", "ENSINO MÉDIO COMPLETO", 
                                          "ENSINO SUPERIOR INCOMPLETO", "ENSINO SUPERIOR COMPLETO", 
                                          "PÓS-GRADUAÇÃO/MBA", "MESTRADO", "DOUTORADO"])
        self.escolaridade_input.setEditable(True)
        self.tem_ctps_input = QComboBox()
        self.tem_ctps_input.addItems(["SIM", "NÃO"])
        self.tem_ctps_input.setEditable(True)
        self.funcao_input = QComboBox()
        self.funcao_input.setEditable(True)
        # depois de criar todos os widgets, carregue as funções:
        funcoes = self.curriculo_model.listar_funcao()
        if funcoes:
            self.funcao_input.addItems(funcoes)
        self.anos_experiencia_input = QSpinBox()
        self.anos_experiencia_input.setRange(0, 50)
        self.meses_experiencia_input = QSpinBox()
        self.meses_experiencia_input.setRange(0, 11)
        self.cep_input = QLineEdit()
        self.pcd_input = QComboBox()
        self.pcd_input.addItems(["SIM", "NÃO"])

        # Adicionando os campos ao layout com grid
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

        # Organizando os campos no layout grid
        row = 0
        for label, widget in fields:
            layout.addWidget(QLabel(label), row, 0)  # Adiciona o label na primeira coluna
            layout.addWidget(widget, row, 1)  # Adiciona o widget na segunda coluna
            row += 1

        # Botões
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("SALVAR")
        self.save_button.clicked.connect(self.save_changes)
        self.cancel_button = QPushButton("CANCELAR")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout, row, 0, 1, 2)  # Botões ocupam duas colunas

        # Configurar navegação com Enter
        self.configurar_transicao_enter([widget for _, widget in fields] + [self.save_button])

        # Definindo cor do texto da data de nascimento, caso haja algum problema de visibilidade
        self.data_nascimento_input.setStyleSheet("color: black;")  # Garantindo que o texto será visível

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
        from datetime import datetime, date
        try:
            curriculo = self.curriculo_model.get_curriculo_by_id(self.curriculo_id)
            experiencias = self.curriculo_model.fetch_experiencias(self.curriculo_id)

            if curriculo:
                self.nome_input.setText(curriculo.get("nome", ""))
                self.cpf_input.setText(curriculo.get("cpf", ""))
                self.sexo_input.setCurrentText(curriculo.get("sexo", ""))

                # Converter data de nascimento para o formato DD/MM/AAAA, verificando o tipo
                data_nascimento = curriculo.get("data_nascimento", "")
                if data_nascimento:
                    if isinstance(data_nascimento, date):
                        data_formatada = data_nascimento.strftime("%d/%m/%Y")
                        self.data_nascimento_input.setText(data_formatada)
                    else:
                        try:
                            date_obj = datetime.strptime(data_nascimento, "%Y-%m-%d")
                            data_formatada = date_obj.strftime("%d/%m/%Y")
                            self.data_nascimento_input.setText(data_formatada)
                        except ValueError:
                            self.data_nascimento_input.setText("")
                else:
                    self.data_nascimento_input.setText("")

                self.telefone_input.setText(curriculo.get("telefone", ""))
                self.telefone_extra_input.setText(curriculo.get("telefone_extra", ""))
                self.cidade_input.setCurrentText(curriculo.get("cidade", ""))
                self.escolaridade_input.setCurrentText(curriculo.get("escolaridade", ""))
                self.tem_ctps_input.setCurrentText("SIM" if curriculo.get("tem_ctps") else "NÃO")
                self.cep_input.setText(curriculo.get("cep", ""))
                self.pcd_input.setCurrentText("SIM" if curriculo.get("pcd") else "NÃO")

                # Preencher o campo "FUNÇÃO" com o valor cadastrado
                if experiencias and len(experiencias) > 0:
                    funcao_id = experiencias[0].get("funcao_id")
                    if funcao_id:
                        query = "SELECT nome FROM funcoes WHERE id = %s;"
                        result = self.curriculo_model.db.execute_query(query, (funcao_id,), fetch_one=True)
                        funcao_nome = result.get("nome") if result else ""
                    else:
                        funcao_nome = ""
                    self.funcao_input.setCurrentText(funcao_nome)
                else:
                    self.funcao_input.setCurrentText(curriculo.get("funcao", ""))
                    
                # Preencher os campos de experiência, se aplicável
                if experiencias and len(experiencias) > 0:
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
            fields = [
                self.nome_input, self.cpf_input, self.sexo_input, self.data_nascimento_input,
                self.telefone_input, self.telefone_extra_input, self.cidade_input,
                self.escolaridade_input, self.tem_ctps_input,
                self.funcao_input, self.anos_experiencia_input,
                self.meses_experiencia_input, self.cep_input, self.pcd_input
            ]

            if source in fields:
                current_index = fields.index(source)
                next_index = current_index + 1
                if next_index < len(fields):
                    fields[next_index].setFocus()
                else:
                    self.save_button.click()
                return True

        return super().eventFilter(source, event)

    def save_changes(self):
        """
        Salva as alterações no banco de dados com os novos campos.
        """
        from datetime import datetime

        nome = self.nome_input.text().strip()
        cpf = self.cpf_input.text().strip()
        sexo = self.sexo_input.currentText()
        
        # Converter data digitada no formato "DD/MM/AAAA" para "yyyy-MM-dd"
        data_text = self.data_nascimento_input.text().strip()
        try:
            date_obj = datetime.strptime(data_text, "%d/%m/%Y")
            data_nascimento = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            data_nascimento = ""
        
        telefone = self.telefone_input.text().strip()
        telefone_extra = self.telefone_extra_input.text().strip()
        cidade = self.cidade_input.currentText()
        escolaridade = self.escolaridade_input.currentText()
        tem_ctps = self.tem_ctps_input.currentText() == "SIM"
        pcd = self.pcd_input.currentText() == "SIM"
        cep = self.cep_input.text().strip()

        if not nome or not cpf or not telefone or not cidade:
            QMessageBox.warning(self, "AVISO", "CAMPOS OBRIGATÓRIOS: NOME, CPF, TELEFONE E CIDADE.")
            return

        try:
            cidade_id = self.curriculo_model.obter_cidade_id(cidade)
            if not cidade_id:
                raise ValueError("CIDADE NÃO ENCONTRADA")

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
                pcd
            )

            QMessageBox.information(self, "SUCESSO", "CURRÍCULO ATUALIZADO!")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "ERRO", f"FALHA AO SALVAR: {str(e)}")