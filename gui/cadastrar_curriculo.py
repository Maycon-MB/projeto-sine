from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QGridLayout, QSpinBox, QComboBox, QDateEdit, QCheckBox
)
from PySide6.QtCore import Qt, QEvent, QDate
from PySide6.QtGui import QKeyEvent, QIcon
import re
from models.curriculo_model import CurriculoModel


class CadastroWidget(QWidget):
    def __init__(self, db_connection):
        """
        Inicializa o widget de cadastro.
        :param db_connection: Conexão com o banco de dados.
        """
        super().__init__()
        self.db_connection = db_connection
        self.curriculo_model = CurriculoModel(self.db_connection)
        self.setup_ui()

    def setup_ui(self):
        """
        Configura a interface do usuário para o formulário de cadastro de currículo.
        """
        self.experiencia_count = 0
        self.max_experiencias = 99

        main_layout = QVBoxLayout(self)

        # Título
        title_label = QLabel("CADASTRO DE CURRÍCULO")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 30px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Formulário
        form_layout = QGridLayout()
        form_layout.setSpacing(15)

        self.cpf_input = self.create_line_edit("DIGITE O CPF (APENAS NÚMEROS)", "CPF:", form_layout, 0, mask="000.000.000-00")
        
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

        # Experiência Section
        experiencia_label = QLabel("EXPERIÊNCIA")
        experiencia_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 15px;")
        form_layout.addWidget(experiencia_label, 9, 0, 1, 2)

        # Checkbox de Primeiro Emprego
        self.primeiro_emprego_input = QCheckBox("")
        form_layout.addWidget(QLabel("PRIMEIRO EMPREGO / JOVEM APRENDIZ :"), 10, 0)
        form_layout.addWidget(self.primeiro_emprego_input, 10, 1)

        # Layout para experiências
        self.experiencias_layout = QVBoxLayout()
        form_layout.addLayout(self.experiencias_layout, 11, 0, 1, 2)

        # Ajustando o botão "ADICIONAR EXPERIÊNCIA"
        self.add_experiencia_button = QPushButton(" + ADICIONAR EXPERIÊNCIA")
        self.add_experiencia_button.setFixedSize(220, 40)  # Define tamanho fixo menor
        self.add_experiencia_button.clicked.connect(self.add_experiencia)
        form_layout.addWidget(self.add_experiencia_button, 12, 0, 1, 2)

        self.servico_input = self.create_combo_box("SERVIÇO:", ["SINE", "MANUAL"], form_layout, 13)

        self.vaga_encaminhada_input = QCheckBox("")
        form_layout.addWidget(QLabel("VAGA ENCAMINHADA :"), 14, 0)
        form_layout.addWidget(self.vaga_encaminhada_input, 14, 1)

        main_layout.addLayout(form_layout)


        self.cadastrar_button = QPushButton("CADASTRAR")
        self.cadastrar_button.clicked.connect(self.cadastrar_dados)
        self.cadastrar_button.setFixedSize(320, 60)  # Define um tamanho menor
        self.cadastrar_button.setStyleSheet("background-color: #0073CF; color: white; padding: 10px; font-size: 16px;")
        self.cadastrar_button.installEventFilter(self)

        self.limpar_button = QPushButton("LIMPAR")
        self.limpar_button.clicked.connect(self.limpar_formulario)
        self.limpar_button.setFixedSize(320, 60)  # Define um tamanho menor
        self.limpar_button.setStyleSheet("background-color: #dcdcdc; color: black; padding: 10px; font-size: 16px;")

        # Organizando os botões lado a lado
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.cadastrar_button)
        button_layout.addWidget(self.limpar_button)
        button_layout.setAlignment(Qt.AlignCenter)  # Centraliza os botões
        main_layout.addLayout(button_layout)

        # Adiciona experiência inicial
        self.add_experiencia()

        # Configura a ordem de tabulação
        self.configure_tab_order()

    def create_line_edit(self, placeholder, label, layout, row, mask=None):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setStyleSheet("font-size: 16px; height: 30px; text-transform: uppercase;")
        line_edit.installEventFilter(self)

        # Converte automaticamente o texto para maiúsculo enquanto o usuário digita
        line_edit.textChanged.connect(lambda text: line_edit.setText(text.upper()))

        # Armazena a máscara, mas só aplica ao sair do campo
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
        spin_box.setStyleSheet("font-size: 16px; height: 30px;")
        spin_box.installEventFilter(self)
        
        placeholder_label = QLabel("Apenas Números")
        placeholder_label.setStyleSheet("color: gray; font-size: 14px; position: absolute;")
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
        combo_box.setStyleSheet("font-size: 16px; height: 30px;")

        # Verifica se options é uma função, e chama-a para obter os valores
        if callable(options):
            options = options()

        # Certifique-se de que options seja uma lista de strings
        if isinstance(options, list) and len(options) > 0 and isinstance(options[0], tuple):
            options = [item[0] for item in options]

        combo_box.addItems(options)  # Adicionando as opções passadas

        combo_box.installEventFilter(self)  # Captura Enter no ComboBox
        if combo_box.isEditable():
            combo_box.lineEdit().installEventFilter(self)  # Captura Enter no LineEdit interno
            combo_box.lineEdit().textChanged.connect(lambda text: combo_box.lineEdit().setText(text.upper()))  # Uppercase automático

        layout.addWidget(QLabel(label), row, 0)  # Adiciona o label
        layout.addWidget(combo_box, row, 1)      # Adiciona o combo_box no layout
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
        """
        Adiciona um novo campo para experiência, incluindo um checkbox para CTPS.
        """
        layout = QHBoxLayout()
        cargo_input = QLineEdit()
        cargo_input.setPlaceholderText("CARGO")
        cargo_input.setStyleSheet("font-size: 16px; height: 30px;")

        # Converte o texto para maiúsculo enquanto o usuário digita
        cargo_input.textChanged.connect(lambda text: cargo_input.setText(text.upper()))

        anos_input = QSpinBox()
        anos_input.setRange(0, 50)
        anos_input.setSuffix(" ANO(S)")
        anos_input.setStyleSheet("font-size: 16px; height: 30px;")

        meses_input = QSpinBox()
        meses_input.setRange(0, 11)
        meses_input.setSuffix(" MÊS(ES)")
        meses_input.setStyleSheet("font-size: 16px; height: 30px;")

        ctps_checkbox = QCheckBox("CTPS")

        remove_button = QPushButton("REMOVER")
        remove_button.clicked.connect(lambda: self.remove_experiencia(layout))

        layout.addWidget(QLabel("CARGO:"))
        layout.addWidget(cargo_input)
        layout.addWidget(QLabel("ANOS:"))
        layout.addWidget(anos_input)
        layout.addWidget(QLabel("MESES:"))
        layout.addWidget(meses_input)
        layout.addWidget(ctps_checkbox)
        layout.addWidget(remove_button)

        self.experiencias_layout.addLayout(layout)
        self.experiencia_count += 1

        # Instalar o filtro de eventos para Enter funcionar como Tab
        cargo_input.installEventFilter(self)
        anos_input.installEventFilter(self)
        meses_input.installEventFilter(self)
        ctps_checkbox.installEventFilter(self)
        remove_button.installEventFilter(self)

        # Atualizar ordem de tabulação
        self.configure_tab_order()

    def remove_experiencia(self, layout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.experiencias_layout.removeItem(layout)
        self.experiencia_count -= 1

    def obter_id_cidade(self, nome_cidade):
        query = "SELECT id FROM public.cidades WHERE nome = %s"
        resultado = self.db.execute_query(query, (nome_cidade,), fetch_one=True)
        if resultado:
            return resultado['id']
        else:
            raise ValueError("Cidade não encontrada.")

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
            vaga_encaminhada = self.vaga_encaminhada_input.isChecked()
            servico = self.servico_input.currentText().upper()
            primeiro_emprego = self.primeiro_emprego_input.isChecked()
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
                cargo_input = layout.itemAt(1).widget()
                anos_input = layout.itemAt(3).widget()
                meses_input = layout.itemAt(5).widget()

                cargo = cargo_input.text().strip()
                anos = anos_input.value()
                meses = meses_input.value()

                if not cargo:
                    QMessageBox.warning(self, "Erro", f"Experiência {i + 1}: Cargo não pode estar vazio.")
                    return

                if meses < 0 or meses > 11:
                    QMessageBox.warning(self, "Erro", f"Experiência {i + 1}: Meses deve estar entre 0 e 11.")
                    return

                # Adiciona a experiência como tupla (cargo, anos, meses)
                experiencias.append((cargo.upper(), anos, meses))

            # Insere os dados no banco
            self.curriculo_model.insert_curriculo(
                nome=nome,
                cpf=cpf_numerico,
                sexo=sexo,
                data_nascimento=data_nascimento,
                cidade_id=cidade_id,
                telefone=telefone,
                telefone_extra=telefone_extra,
                escolaridade=escolaridade,
                vaga_encaminhada=vaga_encaminhada,
                tem_ctps=any(anos > 0 or meses > 0 for _, anos, meses in experiencias),
                experiencias=experiencias,
                servico=servico,
                primeiro_emprego=primeiro_emprego,
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
        self.nome_input.clear()
        self.sexo_input.setCurrentIndex(0)
        self.data_nascimento_input.clear()  # Limpa o campo de data
        self.cidade_input.setCurrentIndex(0)
        self.telefone_input.clear()
        self.telefone_extra_input.clear()
        self.escolaridade_input.setCurrentIndex(0)
        self.servico_input.setCurrentIndex(0)
        self.vaga_encaminhada_input.setChecked(False)
        self.primeiro_emprego_input.setChecked(False)  # Reseta o checkbox para desmarcado
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
            cargo_input = layout.itemAt(1).widget()
            anos_input = layout.itemAt(3).widget()
            meses_input = layout.itemAt(5).widget()

            self.setTabOrder(previous_widget, cargo_input)
            self.setTabOrder(cargo_input, anos_input)
            self.setTabOrder(anos_input, meses_input)

            previous_widget = meses_input  # Atualiza o último widget na cadeia

        # Configurar o último campo para seguir com a ordem
        self.setTabOrder(previous_widget, self.servico_input)
        self.setTabOrder(self.servico_input, self.cadastrar_button)

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