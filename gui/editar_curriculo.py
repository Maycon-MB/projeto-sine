from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QComboBox, QMessageBox, QPushButton, QDateEdit
)
from PySide6.QtCore import Qt, QDate
from models.curriculo_model import CurriculoModel

class EditDialog(QDialog):
    def __init__(self, curriculo_model, curriculo_id, parent=None):
        super().__init__(parent)
        self.curriculo_model = curriculo_model
        self.curriculo_id = curriculo_id

        self.setWindowTitle("EDITAR CURRÍCULO")
        self.setup_ui()
        self.load_curriculo_data()

    def setup_ui(self):
        self.setLayout(QVBoxLayout())

        # Campos para edição
        self.nome_input = QLineEdit()
        self.cpf_input = QLineEdit()
        self.sexo_input = QComboBox()
        self.sexo_input.addItems(["MASCULINO", "FEMININO"])
        self.data_nascimento_input = QDateEdit(calendarPopup=True)
        self.data_nascimento_input.setDisplayFormat("dd/MM/yyyy")
        self.telefone_input = QLineEdit()
        self.telefone_extra_input = QLineEdit()
        self.cidade_input = QComboBox()
        self.escolaridade_input = QComboBox()
        self.escolaridade_input.addItems([
            "ENSINO FUNDAMENTAL", "ENSINO MÉDIO INCOMPLETO", "ENSINO MÉDIO COMPLETO",
            "ENSINO SUPERIOR INCOMPLETO", "ENSINO SUPERIOR COMPLETO", "PÓS-GRADUAÇÃO/MBA",
            "MESTRADO", "DOUTORADO"
        ])
        self.tem_ctps_input = QComboBox()
        self.tem_ctps_input.addItems(["SIM", "NÃO"])
        self.vaga_encaminhada_input = QComboBox()
        self.vaga_encaminhada_input.addItems(["SIM", "NÃO"])
        self.servico_input = QComboBox()
        self.servico_input.addItems(["SINE", "MANUAL"])
        self.cargo_input = QLineEdit()
        self.anos_experiencia_input = QSpinBox()
        self.anos_experiencia_input.setRange(0, 50)
        self.meses_experiencia_input = QSpinBox()
        self.meses_experiencia_input.setRange(0, 11)

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
            ("VAGA ENCAMINHADA", self.vaga_encaminhada_input),
            ("SERVIÇO", self.servico_input),
            ("CARGO", self.cargo_input),
            ("ANOS DE EXPERIÊNCIA", self.anos_experiencia_input),
            ("MESES DE EXPERIÊNCIA", self.meses_experiencia_input)
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

                # Verificando se a data de nascimento é válida
                data_nascimento_str = curriculo.get("data_nascimento", "")
                if isinstance(data_nascimento_str, str) and data_nascimento_str:
                    self.data_nascimento_input.setDate(QDate.fromString(data_nascimento_str, "yyyy-MM-dd"))
                else:
                    self.data_nascimento_input.clear()

                self.telefone_input.setText(curriculo.get("telefone", ""))
                self.telefone_extra_input.setText(curriculo.get("telefone_extra", ""))
                self.cidade_input.addItem(curriculo.get("cidade", ""))
                self.escolaridade_input.setCurrentText(curriculo.get("escolaridade", ""))
                self.tem_ctps_input.setCurrentText("SIM" if curriculo.get("tem_ctps") else "NÃO")
                self.vaga_encaminhada_input.setCurrentText("SIM" if curriculo.get("vaga_encaminhada") else "NÃO")
                self.servico_input.setCurrentText(curriculo.get("servico", ""))

                if experiencias:
                    self.cargo_input.setText(experiencias[0].get("cargo", ""))
                    self.anos_experiencia_input.setValue(experiencias[0].get("anos_experiencia", 0))
                    self.meses_experiencia_input.setValue(experiencias[0].get("meses_experiencia", 0))  # Corrige aqui
                else:
                    self.cargo_input.clear()
                    self.anos_experiencia_input.setValue(0)
                    self.meses_experiencia_input.setValue(0)
            else:
                QMessageBox.warning(self, "AVISO", "CURRÍCULO NÃO ENCONTRADO.")
                self.reject()
        except Exception as e:
            QMessageBox.critical(self, "ERRO", f"ERRO AO CARREGAR DADOS: {e}")
            self.reject()

    def save_changes(self):
        """
        Salva as alterações no banco de dados.
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
        vaga_encaminhada = self.vaga_encaminhada_input.currentText() == "SIM"
        servico = self.servico_input.currentText()
        cargo = self.cargo_input.text().strip()
        anos_experiencia = self.anos_experiencia_input.value()
        meses_experiencia = self.meses_experiencia_input.value()

        # Verifica se os campos obrigatórios estão preenchidos
        if not nome or not cpf or not telefone or not cidade:
            QMessageBox.warning(self, "AVISO", "TODOS OS CAMPOS DEVEM SER PREENCHIDOS.")
            return

        confirmacao = QMessageBox.question(
            self, "CONFIRMAÇÃO", "DESEJA SALVAR AS ALTERAÇÕES?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmacao == QMessageBox.Yes:
            try:
                # Obtém o ID da cidade
                cidade_id = self.curriculo_model.obter_cidade_id(cidade)
                
                # Atualiza os dados do currículo
                self.curriculo_model.update_curriculo(
                    self.curriculo_id, nome, cpf, sexo, data_nascimento, cidade_id,
                    telefone, telefone_extra, escolaridade, vaga_encaminhada, tem_ctps, servico
                )

                # Atualiza as experiências (com limpeza e reinserção ou UPSERT)
                self.curriculo_model.insert_experiencias(
                    self.curriculo_id, [(cargo, anos_experiencia, meses_experiencia)]
                )

                QMessageBox.information(self, "SUCESSO", "CURRÍCULO ATUALIZADO COM SUCESSO!")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "ERRO", f"ERRO AO SALVAR ALTERAÇÕES: {e}")
