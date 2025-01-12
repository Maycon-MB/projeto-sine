from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QGridLayout, QSpinBox, QComboBox
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeyEvent, QIcon
import re
from database.connection import DatabaseConnection
from database.curriculo_model import CurriculoModel

class CadastroWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.db_connection = DatabaseConnection(
            dbname="projeto_sine",
            user="postgres",
            password="admin",
            host="localhost"
        )
        self.curriculo_model = CurriculoModel(self.db_connection)

    def setup_ui(self):
        self.experiencia_count = 0
        self.max_experiencias = 3

        main_layout = QVBoxLayout(self)

        # Título
        title_label = QLabel("Cadastro de Currículo")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 26px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Formulário
        form_layout = QGridLayout()
        form_layout.setSpacing(15)

        self.nome_input = self.create_line_edit("Digite o nome completo", "Nome:", form_layout, 0)
        self.nome_input.textChanged.connect(self.verificar_nome_existente)
        self.nome_status_label = QLabel()
        form_layout.addWidget(self.nome_status_label, 0, 2)

        self.idade_input, self.idade_placeholder = self.create_spin_box("Idade:", form_layout, 1)
        self.telefone_input = self.create_line_edit("Digite o telefone (ex: (XX) XXXXX-XXXX)", "Telefone:", form_layout, 2)
        self.telefone_input.textChanged.connect(self.atualizar_telefone)
        
        self.escolaridade_input = self.create_combo_box("Escolaridade:", form_layout, 3)

        # Área de Experiência
        experiencia_label = QLabel("Experiência")
        experiencia_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 15px;")
        form_layout.addWidget(experiencia_label, 4, 0, 1, 2)

        self.experiencias_layout = QVBoxLayout()
        form_layout.addLayout(self.experiencias_layout, 5, 0, 1, 2)

        self.add_experiencia_button = QPushButton("Adicionar Experiência")
        self.add_experiencia_button.clicked.connect(self.add_experiencia)
        form_layout.addWidget(self.add_experiencia_button, 6, 0, 1, 2)

        main_layout.addLayout(form_layout)

        # Adiciona o campo de experiência inicial
        self.add_experiencia()

        # Botões
        button_layout = QHBoxLayout()
        self.cadastrar_button = QPushButton("Cadastrar")
        self.cadastrar_button.clicked.connect(self.cadastrar_dados)
        self.cadastrar_button.setStyleSheet("background-color: #0073CF; color: white; padding: 10px; font-size: 16px;")
        self.cadastrar_button.setIcon(QIcon("icons/save.png"))

        self.limpar_button = QPushButton("Limpar")
        self.limpar_button.clicked.connect(self.limpar_formulario)
        self.limpar_button.setStyleSheet("background-color: #dcdcdc; color: black; padding: 10px; font-size: 16px;")
        self.limpar_button.setIcon(QIcon("icons/clear.png"))

        button_layout.addWidget(self.cadastrar_button)
        button_layout.addWidget(self.limpar_button)
        main_layout.addLayout(button_layout)

    def create_line_edit(self, placeholder, label, layout, row):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setStyleSheet("font-size: 16px; height: 30px;")
        line_edit.installEventFilter(self)  # Captura Enter
        line_edit.textChanged.connect(lambda text: line_edit.setText(text.upper()))  # Uppercase automático
        layout.addWidget(QLabel(label), row, 0)
        layout.addWidget(line_edit, row, 1)
        return line_edit

    def create_spin_box(self, label, layout, row):
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        spin_box = QSpinBox()
        spin_box.setRange(0, 120)
        spin_box.setButtonSymbols(QSpinBox.NoButtons)
        spin_box.setStyleSheet("font-size: 16px; height: 30px;")
        spin_box.installEventFilter(self)
        
        placeholder_label = QLabel("apenas números")
        placeholder_label.setStyleSheet("color: gray; font-size: 14px; position: absolute;")
        placeholder_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        spin_box.valueChanged.connect(lambda: placeholder_label.setVisible(spin_box.value() == 0))

        container_layout.addWidget(spin_box)
        container_layout.addWidget(placeholder_label)

        layout.addWidget(QLabel(label), row, 0)
        layout.addWidget(container, row, 1)
        return spin_box, placeholder_label

    def create_combo_box(self, label, layout, row):
        combo_box = QComboBox()
        combo_box.setEditable(True)
        combo_box.setStyleSheet("font-size: 16px; height: 30px;")
        combo_box.addItems([
            "ENSINO FUNDAMENTAL",
            "ENSINO MÉDIO INCOMPLETO",
            "ENSINO MÉDIO COMPLETO",
            "ENSINO SUPERIOR INCOMPLETO",
            "ENSINO SUPERIOR COMPLETO",
            "PÓS-GRADUAÇÃO/MBA",
            "MESTRADO",
            "DOUTORADO"
        ])
        combo_box.installEventFilter(self)  # Captura Enter no ComboBox
        if combo_box.isEditable():
            combo_box.lineEdit().installEventFilter(self)  # Captura Enter no LineEdit interno
            combo_box.lineEdit().textChanged.connect(lambda text: combo_box.lineEdit().setText(text.upper()))  # Uppercase automático
        
        layout.addWidget(QLabel(label), row, 0)
        layout.addWidget(combo_box, row, 1)
        return combo_box

    def verificar_nome_existente(self):
        """
        Verifica em tempo real se o nome já está cadastrado no banco.
        """
        nome = self.nome_input.text().strip()
        if len(nome.split()) < 2:  # Certifica-se de que o nome é completo
            self.nome_status_label.setText("Digite o nome completo.")
            self.nome_status_label.setStyleSheet("color: orange;")
            return

        try:
            if self.curriculo_model.is_duplicate_nome(nome):  # Verifica duplicidade pelo nome
                self.nome_status_label.setText("Nome já cadastrado.")
                self.nome_status_label.setStyleSheet("color: red;")
            else:
                self.nome_status_label.setText("Nome disponível.")
                self.nome_status_label.setStyleSheet("color: green;")
        except Exception as e:
            self.nome_status_label.setText("Erro ao verificar nome.")
            self.nome_status_label.setStyleSheet("color: orange;")



    def add_experiencia(self):
        if self.experiencia_count >= self.max_experiencias:
            QMessageBox.warning(self, "Erro", "Você pode adicionar no máximo 3 experiências.")
            return

        layout = QHBoxLayout()
        cargo_input = QLineEdit()
        cargo_input.setPlaceholderText("Cargo")
        cargo_input.setStyleSheet("font-size: 16px; height: 30px;")
        cargo_input.installEventFilter(self)
        cargo_input.textChanged.connect(lambda text: cargo_input.setText(text.upper()))  # Uppercase automático

        tempo_input = QSpinBox()
        tempo_input.setRange(0, 50)
        tempo_input.setSuffix(" ano(s)")
        tempo_input.setStyleSheet("font-size: 16px; height: 30px;")
        tempo_input.installEventFilter(self)

        remove_button = QPushButton("Remover")
        remove_button.setStyleSheet("font-size: 16px; height: 30px;")
        remove_button.clicked.connect(lambda: self.remove_experiencia(layout))

        layout.addWidget(QLabel(f"Cargo {self.experiencia_count + 1}:", self))
        layout.addWidget(cargo_input)
        layout.addWidget(QLabel("Tempo:", self))
        layout.addWidget(tempo_input)
        layout.addWidget(remove_button)

        self.experiencias_layout.addLayout(layout)
        self.experiencia_count += 1

    def remove_experiencia(self, layout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.experiencias_layout.removeItem(layout)
        self.experiencia_count -= 1

    def cadastrar_dados(self):
        """
        Cadastro de dados com confirmação caso o nome já esteja duplicado.
        """
        nome = self.nome_input.text().strip()
        idade = self.idade_input.value()
        telefone = self.telefone_input.text().strip()
        escolaridade = self.escolaridade_input.currentText().strip()

        # Coletar experiências
        experiencias = []
        for i in range(self.experiencias_layout.count()):
            layout = self.experiencias_layout.itemAt(i).layout()
            cargo = layout.itemAt(1).widget().text().strip()
            tempo = layout.itemAt(3).widget().value()
            if cargo:  # Apenas adicionar experiências com cargos preenchidos
                experiencias.append((cargo, tempo))

        if not nome or not telefone or not escolaridade:
            QMessageBox.warning(self, "Erro", "Por favor, preencha todos os campos obrigatórios.")
            return

        if not self.validar_telefone(telefone):
            QMessageBox.warning(self, "Erro", "Telefone inválido! Use o formato (XX) XXXXX-XXXX.")
            return

        try:
            # Verificar duplicidade no banco
            if self.curriculo_model.is_duplicate_nome(nome):
                resposta = QMessageBox.question(
                    self,
                    "Confirmação",
                    "O nome já está cadastrado. Deseja continuar?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if resposta == QMessageBox.No:
                    return

            # Inserir currículo
            curriculo_id = self.curriculo_model.insert_curriculo(nome, idade, telefone, escolaridade)

            # Inserir experiências, se houver
            if experiencias:
                self.curriculo_model.insert_experiencias(curriculo_id, experiencias)

            QMessageBox.information(self, "Sucesso", "Dados cadastrados com sucesso!")
            self.limpar_formulario()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao cadastrar os dados: {e}")



    def limpar_formulario(self):
        resposta = QMessageBox.question(
            self, "Confirmação", "Deseja realmente limpar o formulário?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resposta == QMessageBox.Yes:
            self.nome_input.clear()
            self.idade_input.setValue(0)  # Reseta o valor do QSpinBox para 0
            self.telefone_input.clear()
            self.escolaridade_input.setCurrentIndex(0)
            while self.experiencias_layout.count():
                layout = self.experiencias_layout.takeAt(0).layout()
                self.remove_experiencia(layout)
            self.add_experiencia()  # Reinsere o campo inicial obrigatório

    def validar_telefone(self, telefone):
        pattern = r"^\(\d{2}\) \d{4,5}-\d{4}$"
        return re.match(pattern, telefone)

    def atualizar_telefone(self, texto):
        self.telefone_input.blockSignals(True)
        formatado = self.formatar_telefone(texto)
        print(f"Telefone formatado: {formatado}")  # Debug
        self.telefone_input.setText(formatado)
        self.telefone_input.blockSignals(False)

    def formatar_telefone(self, valor_atual):
        # Remove todos os caracteres não numéricos
        valor_formatado = ''.join(filter(str.isdigit, valor_atual))

        # Se o número de telefone tiver 11 dígitos (formato padrão com DDD e dígito extra)
        if len(valor_formatado) == 11:
            return f'({valor_formatado[:2]}) {valor_formatado[2:7]}-{valor_formatado[7:]}'
        # Se o número de telefone tiver 10 dígitos (formato padrão com DDD sem dígito extra)
        elif len(valor_formatado) == 10:
            return f'({valor_formatado[:2]}) {valor_formatado[2:6]}-{valor_formatado[6:]}'
        # Se o número de telefone tiver 8 ou 9 dígitos (sem DDD)
        elif len(valor_formatado) in (8, 9):
            return f'{valor_formatado[:len(valor_formatado)-4]}-{valor_formatado[-4:]}'
        # Retorna o valor não formatado caso o tamanho seja inválido
        return valor_atual


    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and isinstance(event, QKeyEvent):
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if source == self.escolaridade_input:
                    # Mover o foco diretamente para o campo cargo1
                    if self.experiencias_layout.count() > 0:
                        primeiro_experiencia_layout = self.experiencias_layout.itemAt(0).layout()
                        cargo1_input = primeiro_experiencia_layout.itemAt(1).widget()  # O campo de cargo1
                        if cargo1_input:
                            cargo1_input.setFocus()
                            return True
                else:
                    self.focusNextPrevChild(True)
                    return True
        return super().eventFilter(source, event)

