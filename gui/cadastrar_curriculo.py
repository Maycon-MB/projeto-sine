from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy, QFormLayout, QLineEdit,
    QPushButton, QHBoxLayout, QMessageBox, QGridLayout, QSpinBox,
    QComboBox, QDateEdit, QCheckBox, QScrollArea
)
from PySide6.QtCore import Qt, QEvent, QDate
from PySide6.QtGui import QKeyEvent, QIcon
import re
from models.curriculo_model import CurriculoModel
from gui.busca_cep import consultar_cep

class CadastroWidget(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.curriculo_model = CurriculoModel(self.db_connection)
        self.setup_ui()

    def setup_ui(self):
        self.experiencia_count = 0
        self.max_experiencias = 3
        self.funcoes = self.carregar_funcoes()

        # Layout principal
        main_layout = QVBoxLayout(self)

        # Criando a área de rolagem
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Criando o widget container para o conteúdo dentro da área de rolagem
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Título
        title_label = QLabel("CADASTRO DE CURRÍCULO")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 2em; font-weight: bold; margin-bottom: 10px;")
        content_layout.addWidget(title_label)

        # Formulário
        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        self.cpf_input = self.create_line_edit("DIGITE O CPF (APENAS NÚMEROS)", "CPF:", form_layout, 0, mask="000.000.000-00")
        self.cpf_status_label = QLabel("")  # Label para feedback do CPF
        form_layout.addWidget(self.cpf_status_label, 0, 2)
        self.cpf_input.textChanged.connect(self.verificar_cpf)  # Conecta o sinal

        self.nome_input = self.create_line_edit("DIGITE O NOME COMPLETO", "NOME COMPLETO:", form_layout, 1)

        self.sexo_input = self.create_combo_box("SEXO:", ["MASCULINO", "FEMININO"], form_layout, 2)

        self.data_nascimento_input = self.create_line_edit("DIGITE A DATA DE NASCIMENTO", "DATA DE NASCIMENTO:", form_layout, 3, mask="00/00/0000")

        self.cep_input = self.create_line_edit("DIGITE O CEP", "CEP:", form_layout, 4, mask="00000-000")

        try:
            cidades_raw = self.curriculo_model.listar_cidades()
            cidades = cidades_raw if cidades_raw else ["SELECIONE UMA CIDADE"]
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao listar cidades: {e}")
            cidades = ["SELECIONE UMA CIDADE"]
        self.cidade_input = self.create_combo_box("CIDADE:", cidades, form_layout, 5)

        self.telefone_input = self.create_line_edit("DIGITE O TELEFONE", "TELEFONE:", form_layout, 6, mask="(00) 00000-0000")

        self.telefone_extra_input = self.create_line_edit("DIGITE O SEGUNDO TELEFONE (OPCIONAL)", "TELEFONE EXTRA:", form_layout, 7, mask="(00) 00000-0000")

        self.escolaridade_input = self.create_combo_box(
            "ESCOLARIDADE:",
            [
                "ENSINO FUNDAMENTAL INCOMPLETO",
                "ENSINO FUNDAMENTAL COMPLETO",
                "ENSINO MÉDIO INCOMPLETO",
                "ENSINO MÉDIO COMPLETO",
                "ENSINO SUPERIOR INCOMPLETO",
                "ENSINO SUPERIOR COMPLETO",
                "PÓS-GRADUAÇÃO/MBA",
                "MESTRADO",
                "DOUTORADO"
            ],
            form_layout, 8
        )

        # Experiência
        experiencia_label = QLabel("EXPERIÊNCIA")
        experiencia_label.setStyleSheet("font-size: 1.5em; font-weight: bold; margin-top: 15px;")
        form_layout.addWidget(experiencia_label, 10, 0, 1, 2)

        self.pcd_input = QCheckBox("")
        form_layout.addWidget(QLabel("PCD :"), 11, 0)
        form_layout.addWidget(self.pcd_input, 11, 1)

        # Layout para experiências
        self.experiencias_layout = QVBoxLayout()
        form_layout.addLayout(self.experiencias_layout, 12, 0, 1, 2)

        self.add_experiencia_button = QPushButton(" + ADICIONAR EXPERIÊNCIA")
        self.add_experiencia_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_experiencia_button.clicked.connect(self.add_experiencia)
        self.add_experiencia_button.setStyleSheet(self._button_stylesheet())
        form_layout.addWidget(self.add_experiencia_button, 13, 0, 1, 2, Qt.AlignCenter)

        content_layout.addLayout(form_layout)

        # Botões
        self.cadastrar_button = QPushButton("CADASTRAR CURRÍCULO")
        self.cadastrar_button.clicked.connect(self.cadastrar_dados)
        self.cadastrar_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cadastrar_button.setStyleSheet(self._button_stylesheet())

        self.limpar_button = QPushButton("LIMPAR FORMULÁRIO")
        self.limpar_button.clicked.connect(self.limpar_formulario)
        self.limpar_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.limpar_button.setStyleSheet(self._button_stylesheet())

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.cadastrar_button)
        button_layout.addWidget(self.limpar_button)
        button_layout.setAlignment(Qt.AlignCenter)
        content_layout.addLayout(button_layout)

        # Adiciona experiência inicial
        self.add_experiencia()

        # Conectar o campo CEP com a função de consulta
        self.cep_input.editingFinished.connect(lambda: consultar_cep(self.cep_input, self.cidade_input))

        # Configura a ordem de tabulação
        self.configure_tab_order()

        # Definir o widget de conteúdo na área de rolagem
        scroll_area.setWidget(content_widget)

        # Adicionar a área de rolagem ao layout principal
        main_layout.addWidget(scroll_area)

    def carregar_funcoes(self):
        try:
            funcoes_raw = self.curriculo_model.listar_funcao()
            return funcoes_raw if isinstance(funcoes_raw, list) else ["SELECIONE UMA FUNÇÃO"]
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao listar funções: {e}")
            return ["SELECIONE UMA FUNÇÃO"]

    def _button_stylesheet(self):
        return """
        QPushButton {
            text-align: center;
            border-radius: 10px; /* Bordas mais arredondadas */
            font-size: 16px; /* Texto menor */
            font-weight: bold;
            color: white;
            border: 2px solid #026bc7; /* Cor da borda */
            background-color: #026bc7;
            padding: 12px 16px; /* Botão menor, com menos espaçamento interno */
            outline: none;
            width: 250px; /* Largura fixa para os botões */
            min-width: 120px; /* Largura mínima do botão */
            max-width: 200px; /* Máxima largura para os botões, se necessário */
        }
        QPushButton:hover {
            background-color: #367dba;
        }
        QPushButton:pressed {
            background-color: #0056A1;
        }
        """

    def create_line_edit(self, placeholder, label, layout, row, mask=None):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setStyleSheet("font-size: 1em; height: 2em; text-transform: uppercase;")
        line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        line_edit.installEventFilter(self)
        line_edit.textChanged.connect(lambda text: line_edit.setText(text.upper()))
        if mask:
            line_edit._custom_mask = mask
        layout.addWidget(QLabel(label.upper()), row, 0)
        layout.addWidget(line_edit, row, 1)
        return line_edit

    def create_spin_box(self, label, layout, row):
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        spin_box = QSpinBox()
        spin_box.setRange(0, 120)
        spin_box.setButtonSymbols(QSpinBox.NoButtons)
        spin_box.setStyleSheet("font-size: 1em; height: 2em;")  # Ajuste de tamanho proporcional
        spin_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Expande horizontalmente
        spin_box.installEventFilter(self)
        placeholder_label = QLabel("Apenas Números")
        placeholder_label.setStyleSheet("color: gray; font-size: 0.9em; position: absolute;")
        placeholder_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        spin_box.valueChanged.connect(lambda: placeholder_label.setVisible(spin_box.value() == 0))
        container_layout.addWidget(spin_box)
        container_layout.addWidget(placeholder_label)
        layout.addWidget(QLabel(label), row, 0)
        layout.addWidget(container, row, 1)
        return spin_box, placeholder_label

    def create_combo_box(self, label, options, layout, row):
        combo_box = QComboBox()
        combo_box.setEditable(True)
        combo_box.setStyleSheet("font-size: 1em; height: 2em;")
        if callable(options):
            options = options()
        if isinstance(options, list) and len(options) > 0 and isinstance(options[0], tuple):
            options = [item[0] for item in options]
        combo_box.addItems(options)
        combo_box.installEventFilter(self)
        if combo_box.isEditable():
            combo_box.lineEdit().installEventFilter(self)
            combo_box.lineEdit().textChanged.connect(lambda text: combo_box.lineEdit().setText(text.upper()))
        layout.addWidget(QLabel(label), row, 0)
        layout.addWidget(combo_box, row, 1)
        return combo_box

    def verificar_cpf(self):
        cpf = self.cpf_input.text().strip()
        cpf_numerico = re.sub(r'\D', '', cpf)

        if len(cpf_numerico) != 11:
            self.cpf_status_label.setText("CPF inválido. Deve conter 11 dígitos.")
            self.cpf_status_label.setStyleSheet("color: red;")
            return

        try:
            if self.curriculo_model.is_duplicate(cpf_numerico):
                self.cpf_status_label.setText("CPF já cadastrado.")
                self.cpf_status_label.setStyleSheet("color: red;")
            else:
                self.cpf_status_label.setText("CPF válido.")
                self.cpf_status_label.setStyleSheet("color: green;")
        except Exception as e:
            self.cpf_status_label.setText(f"Erro ao verificar CPF: {e}")
            self.cpf_status_label.setStyleSheet("color: orange;")

    def add_experiencia(self):
        if self.experiencia_count >= self.max_experiencias:
            QMessageBox.warning(self, "Limite de Experiências", f"Você pode adicionar no máximo {self.max_experiencias} experiências.")
            return

        layout = QHBoxLayout()

        # Adiciona ComboBox para seleção de função
        funcao_combo_box = QComboBox()
        funcao_combo_box.addItems(self.funcoes)  # Usa a lista de funções carregada
        funcao_combo_box.setEditable(True)  # Permite a edição manual
        funcao_combo_box.setStyleSheet("font-size: 1em; height: 2em;")
        funcao_combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Converte texto em maiúsculo ao digitar
        funcao_combo_box.lineEdit().textChanged.connect(lambda text: funcao_combo_box.lineEdit().setText(text.upper()))

        anos_input = QSpinBox()
        anos_input.setRange(0, 50)
        anos_input.setSuffix(" ANO(S)")
        anos_input.setStyleSheet("font-size: 1em; height: 2em;")

        meses_input = QSpinBox()
        meses_input.setRange(0, 11)
        meses_input.setSuffix(" MÊS(ES)")
        meses_input.setStyleSheet("font-size: 1em; height: 2em;")

        ctps_checkbox = QCheckBox("CTPS")

        remove_button = QPushButton("REMOVER")
        remove_button.clicked.connect(lambda: self.remove_experiencia(layout))

        layout.addWidget(QLabel("FUNÇÃO:"))
        layout.addWidget(funcao_combo_box)
        layout.addWidget(QLabel("ANOS:"))
        layout.addWidget(anos_input)
        layout.addWidget(QLabel("MESES:"))
        layout.addWidget(meses_input)
        layout.addWidget(ctps_checkbox)
        layout.addWidget(remove_button)

        self.experiencias_layout.addLayout(layout)
        self.experiencia_count += 1

        # Para garantir a tabulação entre os campos
        funcao_combo_box.installEventFilter(self)
        anos_input.installEventFilter(self)
        meses_input.installEventFilter(self)
        ctps_checkbox.installEventFilter(self)
        remove_button.installEventFilter(self)

        self.configure_tab_order()

    def remove_experiencia(self, layout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.experiencias_layout.removeItem(layout)
        self.experiencia_count -= 1

    def cadastrar_dados(self):
        try:
            # Coleta os dados do formulário principal
            cpf = self.cpf_input.text().strip()
            nome = self.nome_input.text().strip().upper()
            sexo = self.sexo_input.currentText().upper()
            data_nascimento = self.data_nascimento_input.text().strip()
            cidade_nome = self.cidade_input.currentText().upper()
            telefone = self.telefone_input.text().strip()
            telefone_extra = self.telefone_extra_input.text().strip()
            escolaridade = self.escolaridade_input.currentText().upper()
            pcd = self.pcd_input.isChecked()
            cep = self.cep_input.text().strip()

            # Validação de CPF e CEP
            cpf_numerico = re.sub(r'\D', '', cpf)
            if len(cpf_numerico) != 11:
                QMessageBox.warning(self, "Erro", "CPF inválido. Deve conter exatamente 11 dígitos.")
                return

            cep_numerico = re.sub(r'\D', '', cep)
            if len(cep_numerico) != 8:
                QMessageBox.warning(self, "Erro", "CEP inválido. Deve conter exatamente 8 dígitos.")
                return

            # Obtem o ID da cidade
            cidade_id = self.curriculo_model.obter_cidade_id(cidade_nome)
            if not cidade_id:
                QMessageBox.warning(self, "Erro", "Cidade inválida.")
                return

            # Coleta as experiências no formato de tupla
            experiencias = []
            for i in range(self.experiencias_layout.count()):
                layout = self.experiencias_layout.itemAt(i).layout()
                funcao_input = layout.itemAt(1).widget()
                anos_input = layout.itemAt(3).widget()
                meses_input = layout.itemAt(5).widget()

                funcao_nome = funcao_input.currentText().upper()
                funcao_id = self.curriculo_model.obter_funcao_id(funcao_nome)
                if not funcao_id:
                    QMessageBox.warning(self, "Erro", f"Função '{funcao_nome}' não encontrada no banco de dados.")
                    return

                anos = anos_input.value()
                meses = meses_input.value()

                if meses < 0 or meses > 11:
                    QMessageBox.warning(self, "Erro", f"Experiência {i + 1}: Meses deve estar entre 0 e 11.")
                    return

                experiencias.append((funcao_id, anos, meses))  # Insere os dados no banco

            self.curriculo_model.insert_curriculo(
                nome=nome,
                cpf=cpf_numerico,
                sexo=sexo,
                data_nascimento=data_nascimento,
                cidade_id=cidade_id,
                telefone=telefone,
                telefone_extra=telefone_extra,
                escolaridade=escolaridade,
                tem_ctps=any(anos > 0 or meses > 0 for _, anos, meses in experiencias),
                experiencias=experiencias,
                pcd=pcd,
                cep=cep_numerico
            )

            QMessageBox.information(self, "Sucesso", "Currículo cadastrado com sucesso.")
            self.limpar_formulario()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao cadastrar currículo: {e}")

    def limpar_formulario(self):
        """
        Limpa todos os campos do formulário, retornando-os aos valores padrão.
        """
        self.cpf_input.clear()
        self.cpf_status_label.clear()  # Limpa a mensagem de status do CPF
        self.nome_input.clear()
        self.sexo_input.setCurrentIndex(0)
        self.data_nascimento_input.clear()  # Limpa o campo de data
        self.cidade_input.setCurrentIndex(0)
        self.telefone_input.clear()
        self.telefone_extra_input.clear()
        self.escolaridade_input.setCurrentIndex(0)
        self.pcd_input.setChecked(False)  # Reseta o checkbox para desmarcado
        self.cep_input.clear()  # Limpa o campo de CEP

        while self.experiencias_layout.count():
            layout = self.experiencias_layout.takeAt(0).layout()
            self.remove_experiencia(layout)

        self.add_experiencia()

    def configure_tab_order(self):
        self.setTabOrder(self.cpf_input, self.nome_input)
        self.setTabOrder(self.nome_input, self.sexo_input)
        self.setTabOrder(self.sexo_input, self.data_nascimento_input)
        self.setTabOrder(self.data_nascimento_input, self.cep_input)
        self.setTabOrder(self.cep_input, self.cidade_input)  # Ordem do CEP para Cidade
        self.setTabOrder(self.cidade_input, self.telefone_input)
        self.setTabOrder(self.telefone_input, self.telefone_extra_input)
        self.setTabOrder(self.telefone_extra_input, self.escolaridade_input)

        previous_widget = self.escolaridade_input

        # Configuração dinâmica para os campos de experiências
        for i in range(self.experiencias_layout.count()):
            layout = self.experiencias_layout.itemAt(i).layout()
            funcao_input = layout.itemAt(1).widget()
            anos_input = layout.itemAt(3).widget()
            meses_input = layout.itemAt(5).widget()

            self.setTabOrder(previous_widget, funcao_input)
            self.setTabOrder(funcao_input, anos_input)
            self.setTabOrder(anos_input, meses_input)

            previous_widget = meses_input  # Atualiza o último widget na cadeia

        self.setTabOrder(previous_widget, self.cadastrar_button)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and isinstance(event, QKeyEvent):
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if source is self.cadastrar_button:
                    self.cadastrar_button.click()  # Emite o clique do botão
                    return True  # Interrompe o processamento padrão de Enter
                else:
                    self.focusNextPrevChild(True)
                    return True

        # Aplica a máscara ao sair do campo
        if isinstance(source, QLineEdit) and event.type() == QEvent.FocusOut:
            if hasattr(source, "_custom_mask") and source._custom_mask:
                source.setInputMask(source._custom_mask)

        # Remove a máscara temporariamente ao entrar no campo
        elif isinstance(source, QLineEdit) and event.type() == QEvent.FocusIn:
            if hasattr(source, "_custom_mask") and source._custom_mask:
                source.setInputMask("")

        return super().eventFilter(source, event)

    def showEvent(self, event):
        """Coloca o foco no campo de Login quando a janela for exibida."""
        self.cpf_input.setFocus()  # Foca no campo "Usuário ou E-mail"
        super().showEvent(event)  # Chama o evento showEvent da classe base